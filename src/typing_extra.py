import typing  # Used for eval
import inspect
from typing import Type, Any, Literal, Union, Iterable, Callable, Dict, get_origin, get_args


class ValueRange:
    def __init__(self, min_v: Union[float, int, Literal['-∞']], max_v: Union[float, int, Literal['∞']]):
        """
        An object with two values, min and max, that specifies a range in which a value should lie.
        :param min_v: The minimal value. May be -∞ if unlimited.
        :param max_v: The maximum value. May be ∞ if unlimited.
        """
        self.min = min_v
        self.max = max_v


def validate_type(value: Any, value_type: Type) -> bool:
    """
    Validates the type of value.

    :param value: The value to validate.
    :param value_type: The type that the value should have.
    :return: Whether the type check was successful.

    © Simon Felix Conrad 2022
    """
    # Black magic ahead :magic_wand:
    if get_origin(value_type) == Literal:
        return any(repr(value) == repr(literal) for literal in get_args(value_type))
    elif get_origin(value_type) == Union:
        return any(validate_type(value, sub_type) for sub_type in get_args(value_type))
    elif isinstance(value, bytes) or isinstance(value, str) or value_type == str or value_type == bytes:
        return not get_args(value_type) and isinstance(value, value_type)
    elif isinstance(value, Iterable):
        sub_values, sub_types = [*(value if not isinstance(value, dict) else value.items())], [*get_args(value_type)]
        if isinstance(value, dict):
            sub_types = [eval(str(value_type).replace('Dict', 'Tuple', 1))]

        len_wout_optionals = sum(1 for t in sub_types
                                 if not (get_origin(t) == Union and str(get_args(t)[1]) == "<class 'NoneType'>"))
        return (len_wout_optionals <= len(sub_values) <= len(sub_types)
                or len(sub_types) == 1 and len_wout_optionals <= len(sub_values)) and \
            all(validate_type(sub_value, sub_types[[i, 0][len(sub_types) == 1]]) for i, sub_value in enumerate(
                value if not isinstance(value, dict) else value.items()))
    else:
        return isinstance(value, get_origin(value_type) if len(get_args(value_type)) else value_type)


# Source: https://stackoverflow.com/a/12627202
def get_default_args(func: Callable) -> Any:
    """
    Gets the default arguments from a callable.

    :param func: The callable.
    :return: The default arguments
    """
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


from typing import Optional, Iterable, Tuple
if __name__ == "__main__":
    print(validate_type({'F': 'F+F--F+F'}, Dict[str, str]))
    print(validate_type("F", str))
    print(validate_type([('F', 'F+F--F+F')], Iterable[Tuple[str, str]]))
    print(validate_type("auto", Optional[Union[Literal['auto'], float]]))