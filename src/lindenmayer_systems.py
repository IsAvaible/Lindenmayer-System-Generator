import os
from typing import Iterable, Tuple, List, Annotated, Optional, Union, Callable, Literal, Dict
from src.typing_extra import ValueRange
from turtle import Turtle, Screen, tracer, update
from random import randint
from math import floor, ceil
from warnings import warn

# Types
cord_type = Tuple[float, float]
r_cord_type = Tuple[int, int]  # r for rounded
variables_type = Dict[str, Union[str, Tuple[str, bool]]]
fg_color_type = Optional[Union[Tuple[int, int, int],
                               Callable[[float, float, float, int, Union[Tuple[r_cord_type, r_cord_type], None], str,
                                         int],
                         Tuple[int, int, int]]]]


def lindenmayer_system(axiom: str, vars: variables_type, depth: Annotated[int, ValueRange(1, '∞')],
                       angle: float, instant_draw: Optional[bool] = True, fg_color: fg_color_type = (255, 255, 255),
                       bg_color: Optional[Iterable[int]] = (0, 0, 0),
                       compression_factor: Optional[Union[Literal['auto'], float]] = 'auto',
                       step_length: Optional[Annotated[int, ValueRange('-∞', '∞')]] = 10,
                       initial_window_size: Optional[
                           Union[Union[List[int], Tuple[int, int]], Literal['full-screen']]] = None,
                       initial_angle: Optional[float] = 0.0,
                       system_center_cords: Optional[Tuple[int, int]] = (0, 0),
                       _turtle: Optional[Turtle] = None,
                       _screen: Optional[Screen] = None,
                       _mainloop: Optional[bool] = True,
                       _screen_icon: Optional[str] = None,
                       __initial_call: bool = True, __initial_depth: int = None,
                       __static_color: bool = None, __no_draw: bool = False,
                       __extrem_cords: Tuple[cord_type, cord_type] = None) \
        -> Tuple[Turtle, Screen, cord_type, cord_type]:
    """
    A function to draw lindenmayer systems supporting the square bracket syntax and multiple customization options.

    :param axiom: The initial axiom. May contain uppercase letters (variables), "+" (right turn), "-" (left turn),
                  "[" (store turtle position and heading) and "]" (restore stored state).
                  >>> "X"
    :param vars: A dictionary containing one or more variables. A variable has a name
                 (Uppercase letter) as key and a replacement axiom (str) as value. Only the first variable will
                 be treated as a forward instruction. The value may also be a tuple containg the replacement axiom
                 and a boolean that determines whether the variabel should be treated as a forward instruction.
                  >>> {"F": "FF", "X": "F+[[X]-X]-F[-FX]+X"}
    :param depth: A integer specifying the recursion depth of the system.
                  >>> 4
    :param angle: The angle as a float by which should be rotated.
                  >>> 25.0
    :param instant_draw: [optional] Whether the system should be drawn instantly, without progress.
                  >>> True
    :param fg_color: [optional] Either an iterator containg the rgb values of the color or a callable taking
                     these arguments: (x_pos: float, y_pos: float, heading: float, initial_recursion_depth: int,
                     extrem_cords: Tuple[min: Tuple[int,int], max: Tuple[int,int]] (only if the compression_factor
                     is 'auto') else None), variable: str, index: int (index of the current character in the axiom)
                     and returning an iterator with the rgb values [int, int, int].
                  >>> lambda x, y, h, i_d, exc, v, i: (x % 255 // 1, y % 255 // 2, h % 255 // 3)
                     If you don't need the avaible arguments you may capture them with a starred expression.
                  >>> lambda *args: (randint(0, 255) for _ in range(3))
                     Or a plain colour:
                  >>> (122, 255, 122)
    :param bg_color: [optional] An iterator containing the rgb values of the color.
                  >>> (0, 0, 0)
    :param compression_factor: [optional]  By what factor the step length should be decreased scaling with the depth.
                                           May also be 'auto' resulting in the drawing being sized to the screen
                                           dimensions. (May take longer).
                  >>> 'auto'
    :param step_length: [optional] The length of one forward movement by the turtle. May be altered by the compression
                                   factor, if it is set to a value other than 1.0.
                                   step_length = step_length * (compression_factor ** depth)
                  >>> 10
    :param initial_window_size: [optional] The window size as a tuple or list containing height and width or the	
                                           literal 'full-screen' to fit the window to the screensize.
                  >>> (400, 400)
    :param initial_angle: [optional] The inital angle of the turtle. Will cause the drawing to be rotated.
                  >>> 0.0
    :param system_center_cords: [optional] The cordinates of the point which is the center of the system.
                                           (0, 0) equals to the center of the screen, which is the default value.
    :param _turtle: [optional] A turtle.Turtle object.
                  >>> Turtle()
    :param _screen: [optional] A turtle.Screen object.
                  >>> Screen()
    :param _mainloop: [optional] Whether the screen should go into a mainloop at the end of the execution.
    :param _screen_icon: [optional] The relative filepath to an icon for the window.
                  >>> "Resources/icon.ico"
    :param __initial_call: Used by the recursion, do not specify.
    :param __initial_depth: Used by the recursion, do not specify.
    :param __static_color: Used by the recursion, do not specify.
    :param __no_draw: Disables any drawing. Used to auto generate the compression factor, do not specify.
    :param __extrem_cords: The min and max cords are passed down when the compression factor is 'auto', do not specify.

    :return: Turtle, Screen, Tuple[min_x: float, min_y: float], Tuple[max_x: float, max_y: float]
    :rtype: Tuple[Turtle, Screen, Tuple[float, float], Tuple[float, float]]

    © Simon Felix Conrad 2022
    """

    # > Setup starts here <
    if _screen is None:
        _screen = Screen()  # Initialize a screen
        _screen.title("Lindenmayer System")
        if _screen_icon is not None and os.path.isfile(_screen_icon):
            _screen.getcanvas().winfo_toplevel().iconbitmap(_screen_icon)
    if _turtle is None:
        _turtle = Turtle()  # Initialize a turtle
    if depth < 0:  # When the replacement hits the recursion base
        return _turtle, _screen, _turtle.pos(), _turtle.pos()
    if __initial_call or (__no_draw and depth == __initial_depth):
        if instant_draw:
            _turtle.hideturtle()
        _turtle.seth((initial_angle + 90) % 360)  # Sets the heading so that 0 equals north
        _turtle.penup()
        _turtle.goto(*system_center_cords)
        _turtle.pendown()
    if __initial_call:  # Triggers at the top of the recursion stack
        # Validate chars in axiom and variables
        if any(not (len(e := var) == 1 and var.isupper()) for var in vars.keys()):
            raise ValueError(f'Variable name "{e}" is invalid.')
        # Validate variable / axiom integrity
        if any(not (c in vars.keys() or (e := c) in '[]+-') for c in axiom):
            raise ValueError(f'Character "{e}" in axiom is neither one of [,],+,- nor a variable.')
        # Validate variable / variable replacement integrity
        if any(not (e1 := var) or not (e2 := repl) or any(not (c in vars.keys() or (e3 := c) in '[]+-') for c in repl)
               for var, repl in ((k, [i[0], i][isinstance(i, str)]) for k, i in vars.items())):
            raise ValueError(f'Character "{e3}" from the replacement "{e2}" of the variable "{e1}" '
                             f'is neither one of [,],+,- nor a variable.')
        # Validate step length and compression factor
        assert step_length != 0 and compression_factor != 0

        _screen.colormode(255)
        _screen.bgcolor(*bg_color)
        _screen.getcanvas().winfo_toplevel().tkraise()
        __static_color = isinstance(fg_color, Iterable)
        __extrem_cords: Union[Tuple[r_cord_type, r_cord_type], None] = None  # Stores the max and min cords

        # This turtle is used to write informing text during the drawing process
        text_turtle = Turtle()
        text_turtle.hideturtle()
        text_turtle.speed(0)
        # Set the color of the text turtle to the inversion of the bg_color
        text_turtle.color(*(abs(v - 255) for v in bg_color))

        if __static_color:
            # If the color of the turtle is static it is set once and not afterwards during the drawing process.
            _turtle.color(*fg_color)
        if __initial_depth is None:
            __initial_depth = depth
        if instant_draw:
            _turtle.speed(0)  # Sets the speed of the turtle to the highest possible value
            tracer(0, 0)  # Disables screen updates during the drawing process
        else:
            # Resets the tracer, just in case the received screen was preconfigured for instant_draw
            tracer(1, 1)
        if initial_window_size is not None:  # Set the window size
            if initial_window_size == 'full-screen':
                _screen.setup(width=1.0, height=1.0)  # This is the turtle equivalent to windowed full-screen
            else:
                _screen.setup(*initial_window_size)  # Might change if the compression factor is not 'auto'
        else:
            initial_window_size = _screen.window_width(), _screen.window_height()
        # Runs an additional drawing process to get the max and min values for x and y and adjusts the compression
        # factor accordingly.
        if compression_factor == 'auto':
            text_turtle.write("Calculating compression factor...")
            tracer(0, 0)  # Disables screen updates during the compression factor calculation
            min_cord, max_cord = lindenmayer_system(axiom, vars, depth, angle, instant_draw, (0, 0, 0), (0, 0, 0), 1,
                                                    step_length, None, initial_angle, system_center_cords, None,
                                                    _screen, _mainloop,
                                                    None, False, __initial_depth, True, True, None)[2:4]
            # Calculates the factor to fit the drawing to the screen dimensions
            factor = min(_screen.window_width() / max(min_cord[0], max_cord[0], key=abs),
                         _screen.window_height() / max(min_cord[1], max_cord[1], key=abs), key=abs)
            # Adds a bit of spacing to the screen edges (10%)
            factor *= 0.9
            # If the step_length is smaller than zero the drawing is rotated by 180 degrees
            factor *= [-1, 1][step_length > 0]

            # Adjust the step length
            step_length = step_length * factor
            # Calculate the distance between min and max cords
            x_dis, y_dis = [max_cord[d] - min_cord[d] for d in (0, 1)]

            def rnd_from_zero(x: float):
                """
                Function to round to the number that is farther away from zero.
                >>> 0.8 -> 1
                >>> -1.4 -> -2
                :param x: the float to round
                :return: x rounded away from 0
                """
                if x < 0:
                    return floor(x)
                else:
                    return ceil(x)

            text_turtle.clear()  # Removes previously written text of the text turtle

            # Adjusts the starting position of the turtle to fit the drawing into the window
            starting_point = [*(-(min_cord[axis] + [x_dis, y_dis][axis] / 2) * factor for axis in (0, 1))]
            _turtle.penup()
            _turtle.goto(*starting_point)
            _turtle.pendown()

            # Stores the max and min cords
            __extrem_cords = tuple(
                tuple(rnd_from_zero(cor * (1 + (not i))) * ex for i, cor in enumerate(starting_point)) for ex
                in (1, -1))

            print("Finished auto-adjusting compression factor.")
            if not instant_draw:
                tracer(1, 1)  # Re-enables screen updates
        else:
            step_length *= compression_factor ** __initial_depth
        print("Started drawing.")
        if instant_draw:
            text_turtle.write("Drawing...")
    if __no_draw:
        _turtle.speed(0)
        _turtle.penup()
    # > Setup ends here <

    stored_states: List[Tuple[Tuple[float, float], float]] = []
    max_x = max_y = min_x = min_y = 0
    # The fundamental logic of the axiom parser
    for index, char in enumerate(axiom):  # Iterate over each character in the axiom and check its role
        if char == "[":  # An opening bracket stores the current state (position and heading) in a list
            stored_states.append((_turtle.pos(), _turtle.heading()))
        elif char == "]":  # Pops of the upmost turtle state of the list and restores it
            if len(stored_states) == 0:
                raise ValueError(f"Unmatched ] bracket encountered at index {index} while parsing the axiom.")
            _turtle.up()
            stored_pos, stored_head = stored_states.pop()
            _turtle.goto(*stored_pos)  # Restore the position
            _turtle.seth(stored_head)  # Restore the orientation
            if not __no_draw:
                _turtle.down()
        elif char == "+":  # Rotates the turtle left by specified angle
            _turtle.left(angle)
        elif char == "-":  # Rotates the turtle right by specified angle
            _turtle.right(angle)
        elif char.isalpha() and char.isupper():  # The char is a variable
            for var_index, (var, properties) in enumerate(vars.items()):  # Iterate through the variables (with index)
                # Handle variables containing a bool which modifies whether the var is drawn
                replacement, draw = (properties, var_index == 0) if isinstance(properties, str) else properties
                if var == char:  # If the currently checked charakter matches the variable
                    if depth == 0:  # Forward movements are only done when the depth is 0 (full replacement)
                        if draw:  # Some variables may not be drawn and are ignored
                            if not __static_color and not __no_draw:  # Evaluate the provided fg function if existent
                                _turtle.color(*map(int, fg_color(_turtle.pos()[0], _turtle.pos()[1], _turtle.heading(),
                                                                 __initial_depth, __extrem_cords, var, index)))
                            # The actual forward movement
                            _turtle.forward(step_length)
                            # If the extreme cords are already known we can save some comparing workload
                            if __extrem_cords is None:
                                # Check whether the new position is an extreme (min / max)
                                pos = _turtle.pos()
                                max_x, max_y = max(pos[0], max_x), max(pos[1], max_y)
                                min_x, min_y = min(pos[0], min_x), min(pos[1], min_y)

                            if compression_factor != 'auto' and not __no_draw:
                                # Resize the window if the turtle hits the screen-bounds
                                if (width := abs(_turtle.pos()[0])) + 20 >= _screen.window_width() // 2:
                                    _screen.screensize(canvwidth=width * 2 + 20)
                                elif (height := abs(_turtle.pos()[1])) + 20 >= _screen.window_height() // 2:
                                    _screen.screensize(canvheight=height * 2 + 20)
                    else:
                        # Go deeper into the axiom, by using the replacement as axiom
                        ret = lindenmayer_system(replacement, vars, depth - 1, angle, instant_draw, fg_color, bg_color,
                                                 compression_factor, step_length, None, initial_angle,
                                                 system_center_cords, _turtle, _screen, _mainloop,
                                                 None, False, __initial_depth, __static_color, __no_draw,
                                                 __extrem_cords)
                        if __extrem_cords is None:
                            # Check whether the returned cords are an extreme (min / max)
                            min_x, min_y = min(ret[2][0], min_x), min(ret[2][1], min_y)
                            max_x, max_y = max(ret[3][0], max_x), max(ret[3][1], max_y)
                    break  # The variable was found, therefore the loop can be broken
            else:
                raise ValueError(f"Variable {char} was not provided.")
        else:
            raise ValueError(f"Invalid character {char} encountered while parsing the axiom.")

    if __initial_call:
        if instant_draw:
            text_turtle.clear()  # Clears the "Drawing..." text from the screen
            update()  # Renders the drawing hidden by the tracer() function on the screen
        print("Finished drawing.")
        if _mainloop:
            _screen.exitonclick()  # Goes into a mainloop until the screen is clicked

    if len(stored_states) != 0:
        # Source: https://stackoverflow.com/a/3891890/14713868
        warn("An opening square bracket was not closed. This does not cause an exception, but it may not "
             "be intentional. Please review your axiom and the provided variables for correctness. This warning "
             f"was raised while processing the following axiom \"{axiom}\".", SyntaxWarning)

    __extrem_cords = [__extrem_cords, ((min_x, min_y), (max_x, max_y))][__extrem_cords is None]
    return _turtle, _screen, *__extrem_cords


def lindenmayer_system_from_file(filepath: str):
    """
    Runs lindenmayer_system() with arguments specified in a file.
    The arguments should be separated with newlines and be evaluable (security risk, do not load unknown files!)
    :param filepath: The path to the file.
    :return: The return of lindenmayer_system() with the arguments.

    © Simon Felix Conrad 2022
    """
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:  # Read the save-file
            args = [eval(line) for line in f.readlines()]  # Evaluates each line and stores it as an argument
        return lindenmayer_system(*args)
    else:
        raise FileNotFoundError(f"No file with {filepath=}.")


if __name__ == '__main__':
    # lindenmayer_system("X", {"F": "FF", "X": "F[+X][-X]FX"}, 3, 25.7, False, (0, 0, 0), (171, 209, 231),
    #                    initial_window_size=(400, 400))
    # lindenmayer_system("X", {"F": "FF", "X": "F+[[X]-X]-F[-FX]+X"}, 6, 25)
    # lindenmayer_system("FL", {"F": "F", "L": "L+RF+", "R": "-FL-R"}, 14, 90, True)
    lindenmayer_system("F--F--F", {"F": "F+F--F+F"}, 6, 60,
                       fg_color=lambda x, y, h, i, exc, *a: (
                       int((abs(exc[0][0]) + int(x)) / abs(exc[0][0] - exc[1][0]) * 255),
                       int((abs(exc[0][1]) + int(y)) / abs(exc[0][1] - exc[1][1]) * 255), int(h) % 255),
                       initial_window_size=None, _mainloop=False)
    lindenmayer_system("F", {"F": "FF+[+F-F-F]-[-F+F+F]"}, 4, 22.5, True,
                       fg_color=lambda *args: (randint(0, 255) for _ in range(3)),
                       compression_factor=1, step_length=9, system_center_cords=(-180, -180), initial_angle=300)

    # lindenmayer_system_from_file("lindenmayer_system-saves\\SierpinskiTriangle.lindenmayer_system")
