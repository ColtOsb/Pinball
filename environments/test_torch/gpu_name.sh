echo "This should print out the name of the first available GPU."
python3 -c "import torch; print(f'device name [0]:', torch.cuda.get_device_name(0))"
