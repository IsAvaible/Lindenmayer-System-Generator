from src.lindenmayer_systems import lindenmayer_system
from src.input_manager import auto_inputs, rerun_prev
from src.tkinter_io import tk_input_with_icon, tk_output
from time import sleep


def _clear(clear: bool = True) -> bool:
    """
    Function to allow the user to clear the screen after each draw.

    :param clear: Should the window be cleared?

    © Simon Felix Conrad 2022
    """
    return clear


def main():
    icon_path = 'icons/app_icon.ico'
    turtle = screen = None
    run = True
    while run:  # The user may rerun indefinitely
        turtle, screen, *r = auto_inputs(lindenmayer_system, tk_input_with_icon(icon_path), tk_output, True,
                                         kwargs={'_mainloop': False, '_screen_icon': icon_path, '_screen': screen,
                                                 '_turtle': turtle})
        sleep(3)
        # Ask whether the user wants to rerun
        run = auto_inputs(rerun_prev, tk_input_with_icon(icon_path), tk_output, False)
        # Ask whether the user wants to clear the screen before rerunning
        if run and auto_inputs(_clear, tk_input_with_icon(icon_path), tk_output, False):
            turtle.clear()
    screen.getcanvas().winfo_toplevel().tkraise()
    screen.exitonclick()


if __name__ == '__main__':
    main()
