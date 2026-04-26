from .testcase import Testcase
class TorchTest (Testcase):
    torch = None

    def __TestImportTorch():
        import torch
        TorchTest.torch = torch
        return None

    def __TestGPUAvailable():
        return TorchTest.torch.cuda.is_available()

    def __TestDeviceName(device_id):
        return f"Device[{device_id}]: {TorchTest.torch.cuda.get_device_name(device_id)}"
        
    def __TestTorchEnv():
        return TorchTest.torch.utils.collect_env.get_pretty_env_info()

    def Test(device_id=0, print_results=False, return_results=True, output_level=0):

        tests = [
                 ("Importing torch",TorchTest.__TestImportTorch,[]),
                 ("CUDA/GPU Available",TorchTest.__TestGPUAvailable,[]),
                 ("Device Name",TorchTest.__TestDeviceName,[device_id]),
                 ("Torch Env",TorchTest.__TestTorchEnv,[])
                 ]

        return Testcase.RunTests(tests,print_results,return_results,output_level)



if __name__ == "__main__":
    results = TorchTest.Test(print_results=True)
