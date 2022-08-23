import tkinter as tk
import ctypes
from tkinter.messagebox import Message
from typing import Type, Any, Optional, Callable
from idlelib.config import idleConf
from idlelib.colorizer import ColorDelegator
from idlelib.percolator import Percolator
from src.typing_extra import validate_type
from math import floor
from functools import partial
from ctypes import windll


# noinspection PyArgumentList
def _type_check(text: tk.StringVar, param_type: Type, type_widget: tk.Widget) -> None:
    """
    Checks whether the parameter has the right type and changes the colour of the indicating widget accordingly.

    :param text: A StringVar holding the value of the Text field.
    :param param_type: The type of the parameter.
    :param type_widget: The Widget which is used to indicate the state of the type check.
    :return: None

    © Simon Felix Conrad 2022
    """
    red, green = "#ff6961", "#77DD77"
    try:
        ev = eval(text.get())  # The developer responsible for security be screaming .. oh, that's me :)
    except Exception:  # Text doesn't evaluate to a literal / raises an exception when evaluated
        type_widget.configure(background=red)
        return
    type_widget.configure(background=(green if validate_type(ev, param_type) else red))


def tk_input(parameter_name: str, parameter_type: Type, has_default: bool, parameter_default: Any,
             function_name: str, parameter_doc: Optional[str], is_function_param: bool,
             icon_path: str = None) -> str:
    """
    A function to get an user-input for a parameter via tkinter widgets.
    Automatically validates the types of and syntax highlights the input.

    :param parameter_name: The name of the parameter.
    :param parameter_type: The type of the parameter.
    :param has_default: Whether the parameter has a default argument.
    :param parameter_default: The default argument of the parameter.
    :param function_name: The name of the relating function (Used as the title of the window)
    :param parameter_doc: The documentation for the parameter.
    :param is_function_param: Whether the parameter relates to a function or is used for configuration purposes.
                              This slightly changes the prompt label text.
    :param icon_path: The filepath of the icon. For supported formats see: https://stackoverflow.com/a/42706390
    :return: The input of the user as string.

    © Simon Felix Conrad 2022
    """
    windll.shcore.SetProcessDpiAwareness(1)
    win = tk.Tk()
    win.title(f"{function_name}")
    if icon_path is not None:
        win.iconbitmap(icon_path)
        try:
            # Source: https://stackoverflow.com/a/1552105/14713868
            # Set the taskbar icon on Windows OS
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('simon.conrad.prod')
        except Exception:
            pass
    win.resizable(False, False)

    # idleConf.CurrentTheme() < This returns the current idle theme, we override this method to always return IDLE Dark
    # Side note: After digging through the idle source code, you can't imagine how satisfying it felt to figure this out
    idleConf.CurrentTheme = lambda: 'IDLE Dark'
    cd = ColorDelegator()

    sv = tk.StringVar()
    name_label = tk.Label(text=[f'Configurate {parameter_name}',
                                f'Value for parameter {parameter_name}.'][is_function_param], master=win)
    type_label = tk.Label(text=f"Type: {parameter_type}", wraplength=400, master=win)
    text = tk.Text(height=1, width=28,
                   fg=cd.tagdefs['ERROR']['foreground'], bg=cd.tagdefs['KEYWORD']['background'], master=win,
                   insertbackground=cd.tagdefs['ERROR']['foreground'])  # Cursor colour

    parameter_doc = ' '.join((parameter_doc or 'No documentation found.').split()).replace(">>>", "\n>>>")

    doc_label = tk.Label(text=f"{parameter_doc.strip()}", wraplength=300, fg='blue', master=win)

    # Source: https://stackoverflow.com/a/67775442
    Percolator(text).insertfilter(cd)
    sv.trace_add("write", lambda *a: _type_check(sv, parameter_type, type_label))
    for w in (text, win):
        w.bind('<Return>', lambda e: win.quit())

    def on_key_release(e):
        sv.set(text.get("1.0", tk.END).replace("\n", ""))  # Source: https://stackoverflow.com/a/55043283
        text.configure(height=floor((len(sv.get())-1) / 28) + 1)

    text.bind('<KeyRelease>', on_key_release)
    if has_default:
        text.insert(tk.END, repr(parameter_default) if not repr(parameter_default)[1:].startswith(
            'lambda') else parameter_default)
        on_key_release(None)  # Adjust text widget height

    name_label.pack()
    type_label.pack()
    text.pack()
    doc_label.pack()

    win.tkraise()
    win.eval('tk::PlaceWindow . center')  # Source: https://stackoverflow.com/a/10018670

    text.focus_set()
    win.mainloop()

    # This will run after the mainloop breaks
    val = sv.get()
    win.destroy()
    cd.close()
    return val


def tk_input_with_icon(icon_path: str) -> Callable:
    """
    Returns tk_input, but with the icon_path set to the provided string.

    :param icon_path: The filepath of the icon. For supported formats see: https://stackoverflow.com/a/42706390
    :return: :func:`~tkinter_io.tk_input`
    """
    # Source: https://stackoverflow.com/a/17625730/14713868
    return partial(tk_input, icon_path=icon_path)


# Source: https://stackoverflow.com/a/64416478/14713868
def tk_output(title: str, string: str, timeout: float) -> None:
    """
    Temporarily shows a message with a title via a tkinter Message box.

    :param title: The title of the Message box.
    :param string: The content of the Message box.
    :param timeout: [optional] After how much time the Message box should be destroyed automatically.
                               Automatic destruction is disabled if the timeout is below or equal to 0.
    """
    root = tk.Tk()
    root.iconify()
    try:
        if timeout > 0:
            root.after(int(timeout*1000), root.destroy)
        Message(title=title, message=string, master=root).show()
        root.destroy()
    except tk.TclError:
        pass
