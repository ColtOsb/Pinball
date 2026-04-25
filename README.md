# AI Pinball

## Preqrequisites

1. The actual pinball game code must be downloaded and running before the ai code can play the game. Follow the instructions located within [https://github.com/JamesL-dev/wizard#](https://github.com/JamesL-dev/wizard) to download the game and get it running.
2. Sufficiently fast graphics processing power. The camera operates at 30 frames per second, meaning every cycle must occur in 33ms or less. Inference times should be less than 20ms to achieve this. The system used for the demonstration is:

    ``` text
    Operating System: Fedora Linux 43
    KDE Plasma Version: 6.6.4
    KDE Frameworks Version: 6.25.0
    Qt Version: 6.10.3
    Kernel Version: 6.19.11-200.fc43.x86_64 (64-bit)
    Graphics Platform: Wayland
    Processors: 12 × AMD Ryzen 5 5600G with Radeon Graphics
    Memory: 32 GiB of RAM (31.2 GiB usable)
    Graphics Processor: AMD Radeon RX 9060 XT
    Manufacturer: Micro-Star International Co., Ltd.
    Product Name: MS-7C91
    System Version: 3.0
    ```

3. Potentially extra drivers, software, or firmware to enable graphics card detection. Currently, this is either AMD's ROCM suite or Nvidia's CUDA suite. See the providers' documentation for instructions on how to install. This may be unnecessary, as the graphics card was detected out of the box on the demo system. See tools like `rocminfo` and `nvidia-smi` for testing if your card is detected.
4. Install anaconda or another virtual environment manager and create a virtual environment. For the demo, special ROCM versions of pytorch and torchvision had to be installed, which are present in `environment-rocm.yml` and `environment-rocm-strict.yml`. (The only difference between the two is that the strict version strictly sets the version numbers of packages). If using another system, you may need to use the hardware manufacturer's provided libraries. `environment.yml` is more generalized and can be adapted to your system or run before the system specific portions.

