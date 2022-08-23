from typing import Type, Any


def console_input(parameter_name: str, parameter_type: Type, has_default: bool, parameter_default: Any,
                   function_name: str, parameter_doc: str, is_function_param: bool) -> str:
    """
    A function to get a user input for a parameter via the standard input.

    :param parameter_name: The name of the parameter.
    :param parameter_type: The type of the parameter.
    :param has_default: Whether the parameter has a default argument.
    :param parameter_default: The default argument of the parameter.
    :param function_name: The name of the relating function (Used as title of the window)
    :param parameter_doc: The documentation for the parameter.
    :param is_function_param: Whether the parameter relates to a function or is used for configuration purposes.
    :return: The input of the user as string.

    © Simon Felix Conrad 2022
    """
    default_arg_string = ["", f"Default argument = {parameter_default}"][has_default]
    parameter_doc = ' '.join((parameter_doc or 'No documentation found.').split()).replace(">>>", "\n>>>")
    inp = input(
        (f"{parameter_name}: {parameter_doc}\n" if parameter_doc is not None else "") +
        (f"Please input a value for the parameter {parameter_name} of type {parameter_type}. {default_arg_string}... "
            if is_function_param else f"{default_arg_string}... "))
    print("-+-+-+-+-+-+-+-+-+-+-+-+-+-")
    if inp == "" and has_default:
        inp = repr(parameter_default) if not repr(parameter_default)[1:].startswith('lambda') else parameter_default

    return inp


def console_output(title: str, string: str, timeout: float):
    """
    Outputs a message with a title using the standard output.

    :param title: The title of the message.
    :param string: The message.
    :param timeout: Timeout of the message. Not used in this implementation.

    © Simon Felix Conrad 2022
    """
    print(f'{title}: {string}')
