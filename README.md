# AI Pinball

## Preqrequisites

1. The actual pinball game code must be downloaded and running before the ai code can play the game. Follow the instructions located within [https://github.com/JamesL-dev/wizard#](https://github.com/JamesL-dev/wizard) to download the game and get it running.
2. Sufficiently fast graphics processing power. The camera operates at 30 frames per second, meaning every cycle must occur in 33ms or less. Inference times should be less than 20ms to achieve this. The system used for the demonstration an Nvidia Jetson Orin Nano 3.
3. Potentially extra drivers, software, or firmware to enable graphics card detection. Currently, this is either AMD's ROCM suite or Nvidia's CUDA suite. See the providers' documentation for instructions on how to install. See tools like `rocminfo` and `nvidia-smi` for testing if your card is detected.
4. Install anaconda or another virtual environment manager and create a virtual environment. For the demo, special Nvidia versions of pytorch and torchvision had to be installed. `environment.yml` is more generalized and can be adapted to your system or run before the system specific portions.

## Using the code
See [instructions](instructions.md) for an explanation of how to use the pinball machine as it currently is.

## Execution

The program is designed to be invoked by the `__main__.py` script, which takes a position argument to indicate which mode to run in. Execute `__main__.py --help` for a help menu of what the supported arguments are. Currently, the supported modes are:

* `run`: Run the self-playing program, sourcing flipper locations from the model's prediction.
* `demo`: Same as run, but use hard-coded flipper locations.
* `test-torch`: Run various tests to determine if pytorch is installed and the GPU is detected.
* `test-plc`: Run various tests to determine if a connection to the PLC can be established.

## Troubleshooting

* The register that is written to for activating the flippers remotely is different from the one used when pressing a button. At times, the register may be stuck high, such that a flipper is always stuck up, and pressing the button will not lower it. Execute: `control.py` directly to run a program that can write to various registers using the keyboard. The left and right arrows can be used to toggle between low and high on the left and right flippers, respectively. The spacebar will activate the autokicker.
* At times, the PLC may get out of sync from the game program. This can be seen when the flippers are able to be activated when the game is not running. The may also not dispense a ball when the start button is pressed even though the game has been started. This can be fixed by holding the buttons for both flippers simultaneously for around 10 seconds. After the time has elapsed, the flippers will reset back down on their own, the PLC will reset its state, and the game will reset to out of the game.

## Components

Below is the various components used in the project and how to interact with them.

> [!Note]
> References to left, right, top, and bottom are from the perspective of the camera. As it is set up, the camera is rotated 180 degrees from where the player would stand when playing the machine. Thus if a person was standing at the machinie playing it, left would be their right, right would be their left, top would be their bottom, and bottom would be their top.

### PLC

The PLC can be interfaced with by using the `control.py` file. Located within this file is a class that controls establishing a connection with the PLC and exposes various functions for specific tasks. This class should be used directly for all tasks involving the PLC that is not related to the flippers. For finer control of the flippers, the Flipper class within `flipper.py` exists. This class is an abstraction for the flippers. It makes it easier to toggle flippers and ensure that the correct flipper is being controlled. 

### Vision

Vision and frame sourcing is controlled by the class within `VideoCapture.py`. This class returns the current frame and does not buffer any. This is ideal if the system temporarily slows down, as it will not encounter a backlog of frames to process.

### Preprocessing

The model was trained off of frames gathered from the camera after preprocessing has occured. Currently, the only preprocessing that occurs is a perspective transform, which crops and square the image to only include the desired area. The code responsible for the perspective transform is found within `perspective.py`. Creating the transformation matrix requires storing the coordinates for the final cropped image, which should be the inside corners of the pieces of black tape on the side rails of the pinball machine. These coordinates should be stored within `config.py` in the `PerspectiveCalibration` class. The file `coord_finder.py` can be directly executed to run a program that allows you to click on an image to determine the coordinates. These then just need to be input into `config.py`.

### Image collection

The files `datacapture.py` and `datasort.py` are used to save frames from the camera so that they can be annotated and used for training a model.
