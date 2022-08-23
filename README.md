# Lindenmayer System Generator
This application allows the generation of [Lindenmayer systems](https://en.wikipedia.org/wiki/L-system) with a GUI focused on modularity and reusability, aimed at python developers.

By running [main.py](main.py) the following user interface will be opened:

![Image of the user interface](https://i.imgur.com/jl9skuy.png)

The application will guide the user through the different available parameters, providing type hinting, documentation and an example for each one. Parameter values have to be written in python syntax. It is therefore recommended to know the language in order to use this software.

After providing all parameters, the application will start drawing the specified lindenmayer system. This may result in an image like this:

![Image of a lindenmayer system reesembling a plant, with a multi-color gradient](https://i.imgur.com/LyWnR3S.png)

Users may also save and restore previous lindenmayer systems. The application ships with multiple systems to try out (above image uses the "PlantGradient" save-file).


# How to Install
1. Acquire the source code by cloning the repository or downloading and unzipping this [zip file](/../../archive/refs/heads/master.zip).
2. The application requires Python 3.9 or higher to be installed on the host system. To install python, visit
   [Python's official webpage](https://www.python.org/downloads/) and download the latest version. Make sure to check the path option during the installation progress.
3. After finishing these initial steps the application can be run using the [main.py](main.py) file.


# Why the user interface uses Python syntax
Developing GUIs can be a lengthy and exhausting task. The repetitiveness of converting a function into a GUI motivated me to develop a modular system that allows the developer to create an user interface by simply passing a documented and type hinted function to the system. 

While this makes development much faster, it requires users of the program to be able to understand and create values from python types, but also enables complex parameters, like function support for the foreground color of the l-system.



# Contact
If you encounter any bugs during your use or want to submit a feature request, please use the [Issues section](/../../issues).

