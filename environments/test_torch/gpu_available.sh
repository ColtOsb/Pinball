echo "This should print True or False, as to whether torch detects a GPU is available."
python3 -c 'import torch; print(torch.cuda.is_available())'
