import os
import re
import traceback

from typing import Callable, Type, Any, get_type_hints, Dict
from src.typing_extra import validate_type, get_default_args
from functools import partial
from src.console_io import console_input, console_output


def _eval_wrapper(inp: Any, out_fun: Callable[[str, str], None], empty_value: object) -> Any:
    """
    Wraps eval in such way that the empty value is returned upon hitting an exception.

    :param inp: The input to evaluate.
    :param out_fun: The function that is used to output an exception.
    :param empty_value: The empty value.
    :return: Either the evaluated input or the empty value.

    © Simon Felix Conrad 2022
    """
    try:
        return eval(inp)
    except Exception as e:
        out_fun("Couldn't parse input.", f" Exception: {e}")
        return empty_value


def _check_filename(filename: Any, out_fun: Callable[[str, str], None]) -> bool:
    """
    Checks whether the filename is a string and does not contain illegal characters.

    :param filename: Anything.
    :param out_fun: The function used to output an error message.
    :return: Whether the filename is valid.

    © Simon Felix Conrad 2022
    """
    if not isinstance(filename, str):
        out_fun("Error", "The filename has to be a string.")
        return False
    if any(map(lambda char: char in '\\/:*?\"<>|', filename)):
        out_fun("Error", f"The filename contains an invalid character.")
        return False
    return True


def auto_inputs(fun: Callable, inp_fun: Callable[[str, Type, bool, Any, str, str, bool], str] = console_input,
                out_fun: Callable[[str, str, float], None] = console_output, enable_saves: bool = True,
                kwargs: Dict[str, Any] = None, error_message_timeout: float = 2.5) -> Any:
    """
    Automatically creates inputs for a function and validates their types.
    Also allows saving a configuration as a text file and restoring it later.

    ! Will only work if all parameters are type hinted and documentation is written in the reST-format !

    :param fun: The function for which inputs and type validations should be generated.
    :param inp_fun: The function used to input values.
                    Function Parameters: [parameter_name, parameter_type, has_default, parameter_default, function_name,
                        parameter_doc, is_function_param]
    :param out_fun: The function used to output messages, e.g. exceptions.
                    Function Parameters: [title, content, timeout]
    :param enable_saves: Whether it should be possible to save the configuration of the function with text files.
    :param kwargs: Pre-provide keyword arguments that will not be editable by the user.
    :param error_message_timeout: The timeout for error messages during the input process.
    :return: The return of fun with given inputs.

    © Simon Felix Conrad 2022
    """
    types = get_type_hints(fun)
    default_args = get_default_args(fun)
    fun_name = fun.__name__
    inputs, raw_inputs = [], []
    empty_value = object()  # To make the usage of Null values possible
    doc_string = fun.__doc__
    out_fun: Callable[[str, str], None] = partial(out_fun, timeout=error_message_timeout)
    kwargs = {} if kwargs is None else kwargs

    restore = False
    # Checks whether the saves directory exists. If so, checks if there are any save files inside and stores them
    # sorted by date (desc) in a list without their file extension.
    if enable_saves and os.path.isdir(dirpath := f'{fun_name}-saves') \
            and len(files := [*map(lambda f: f.replace(f'.{fun_name}', ''),
                                   sorted(filter(lambda f: f.endswith(f'.{fun_name}'), os.listdir(dirpath)),
                                          key=lambda f: os.stat(f'{dirpath}\\{f}').st_mtime, reverse=True))]) > 0:
        restore = empty_value
        # If there are save-files that can be restored, ask the user whether he wants to make use of this feature
        while restore == empty_value or not isinstance(restore, bool):
            inp = inp_fun("Restore", bool, True, False, fun_name, "Should the configuration be restored from a " +
                                                                  "text file?", False)
            restore = _eval_wrapper(inp, out_fun, empty_value)
            if not (correct_type := validate_type(restore, bool)):
                out_fun("Error", "Type validation failed. Rolling back...")

        if restore:
            while True:
                # Ask the user to input the filename, suggests all possible filenames in the documentation.
                filename = inp_fun("Filename", str, True, files[0], fun_name,
                                   f"Enter the name of the text file.\n>>> Available Files: {'; '.join(files)}", False)
                filename = _eval_wrapper(filename, out_fun, empty_value)

                # Validate the filename
                if not filename == empty_value and _check_filename(filename, out_fun):
                    # Restore the content of the file by evaluating them and stores them as the default args.
                    if os.path.isfile(filepath := f'{dirpath}\\{filename}.{fun_name}'):
                        with open(filepath, 'r') as file:
                            default_args = {k: v for k, v in zip(types.keys(),
                                                                 [eval(line) if not isinstance(eval(line), Callable)
                                                                  else line.strip() for line in file.readlines()])}
                        break
                    else:
                        out_fun("Error", "There exists no file with the given filename.")

    param: str
    param_type: Type
    # Iterates over each parameter with its type
    for param, param_type in types.items():
        if param.startswith("_") or param == "return":
            continue
        if param in kwargs.keys():
            inputs.append(kwargs[param])
            del kwargs[param]
            continue

        # Splits the function doc into parameter segments.
        # The doc is parsed as if it is written in the common reST-format.
        param_doc = re.findall(f":param {param}:[\\S\\s]*?(?::param|$)", doc_string) or None \
            if doc_string is not None else None
        if param_doc is not None:
            param_doc = param_doc[0]
            # Finds the documentation of the parameter
            param_doc = re.sub(f"(:param {param}:|\n.*:param)", "", param_doc)

        correct_type = False
        # User is prompted for input until the argument has the proper type
        while not correct_type:
            has_default_arg = param in default_args.keys()
            default_arg = default_args.get(param, None)

            # User is prompted for input until the evaluation does not fail
            inp = empty_value
            while inp == empty_value:
                inp = inp_fun(param, param_type, has_default_arg, default_arg, fun_name, param_doc, True)
                raw_inp = inp  # The raw input is stored to use it in save-files
                inp = _eval_wrapper(inp, out_fun, empty_value)

            if not (correct_type := validate_type(inp, param_type)):
                out_fun("Error", "Type validation failed. Rolling back...")
            else:
                inputs.append(inp)
                raw_inputs.append(raw_inp)

    if enable_saves:
        save = empty_value
        # Asks the user whether he wants to save the configuration in a save-file
        while save == empty_value or not isinstance(save, bool):
            inp = inp_fun("Save", bool, True, True, fun_name, "Should the configuration be saved in a text file?", False)
            save = _eval_wrapper(inp, out_fun, empty_value)

            if not (correct_type := validate_type(save, bool)):
                out_fun("Error", "Type validation failed. Rolling back...")

        if save:
            while True:
                filename = inp_fun("Filename", str, restore, filename if restore else None,
                                   fun_name, "Please provide a name for the text file.", False)
                filename = _eval_wrapper(filename, out_fun, empty_value)
                # If the provided filename does not contain illegal characters proceeds to store the arguments.
                if not filename == empty_value and _check_filename(filename, out_fun):
                    # and not os.path.isfile(filepath := f'{dirpath}\\{filename}.{fun_name}'):  # No overrides
                    filepath = f'{dirpath}\\{filename}.{fun_name}'
                    if not os.path.isdir(dirpath):  # Create the saves directory if it does not exist yet
                        os.mkdir(dirpath)
                    with open(filepath, 'w+') as file:  # Write the file
                        file.write('\n'.join(map(lambda arg: arg, raw_inputs)))
                    break

    # Returns the return of the function run with the provided arguments
    try:
        return fun(*inputs, **kwargs)
    except Exception:
        out_fun("Runtime Exception", traceback.format_exc(), timeout=-1)
        return None


def rerun_prev(rerun: bool = True):
    """
    Function that can be used after the inputs for a function have been taken with the auto_inputs() function to
    allow the user to rerun the process.

    :param rerun: Would you like to rerun the previous function?
    :param:
    :return: The bool provided with rerun.

    © Simon Felix Conrad 2022
    """
    return rerun


if __name__ == "__main__":
    auto_inputs(rerun_prev)
    # auto_inputs(lindenmayer_system, console_input, console_output)
