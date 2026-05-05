## Credentials
username: pi  
password: pi  
sudo password: pi  

## Instructions

1. Turn on the power bar inside the pinball machine. On the back side of the machine is a large hold in the bottom-left corner. Immediately inside of this whole is a power bar, press the switch on it to provide power to the machine and turn it on.
2. Move to the front of the machine and see if the second head from the left is spinning. If it is not, then power to the PLC is cut off. Move to the right side of the machine and find the power switch underneath and turn it on. Now the head should be spinning and the back-lighting should be on.
3. Wait for everything to boot up. Once completed, a desktop environment will appear.
4. Open a terminal. This can be done by pressing ctrl+alt+t, clicking the icon on the left, or by using the app launcher.
5. Three methods for starting the game exist, and will be listed in order of ease of use:
   1. Type `game` and press enter. This is an alias for method 2 below.
   2. Execute `source /home/pi/wizard/start_wizard.sh`.
   3. Navigate to the game directory: `cd /home/pi/wizard`, activate the virtual environment: `source venv/bin/activate`, then start the game: `source start_wizard.sh`
6. If playing the game manually, you are all done. Skip to step 9 to see how to turn off the machine.
7. If starting the self-playing component, repeat step 4 to open a new terminal. Do not close the existing one. Note that you may have to press the super key or use alt+tab to get out of the game screen without closing it.
8. Two methods for starting the self-playing code exist, and will be listed in order of ease of use:
   1. Type `ai` and press enter. This is an alias for method 2 below.
   2. Navigate to the code directory: `cd /home/pi/pinball`, activate the virtual environment: `source test_env/bin/activate`, then start the game: `python3 __main__.py demo`.
9. To close everything and shut the machine off, follow these steps to ensure it is graceful and to minimize the chance of data corruption.
10. Close the self-playing code (if applicable) by clicking on its terminal and pressing ctrl+c
11. Close the game program by clicking on it and pressing esc
12. Either turn off the machine using the dialog in the top right or enter the following command into a terminal: `sudo shutdown now`
13. Wait for it to shutdown, then turn off the power switch on the back of the machine. The switch under the machine is powered by this one, so only the one in the back needs to be turned off.
