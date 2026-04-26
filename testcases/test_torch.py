from .testcase import Testcase
class TorchTest (Testcase):
    torch = None

    def TestImportTorch():
        import torch
        TorchTest.torch = torch
        return None

    def TestGPUAvailable():
        return TorchTest.torch.cuda.is_available()

    def TestDeviceName(device_id):
        return f"Device[{device_id}]: {TorchTest.torch.cuda.get_device_name(device_id)}"
        
    def TestTorchEnv():
        return TorchTest.torch.utils.collect_env.get_pretty_env_info()

    def Test(device_id=0, print_results=False, return_results=True, output_level=0):

        tests = [
                 ("Importing torch",TorchTest.TestImportTorch,[]),
                 ("CUDA/GPU Available",TorchTest.TestGPUAvailable,[]),
                 ("Device Name",TorchTest.TestDeviceName,[device_id]),
                 ("Torch Env",TorchTest.TestTorchEnv,[])
                 ]

        return Testcase.RunTests(tests,print_results,return_results,output_level)



if __name__ == "__main__":
    results = TorchTest.Test(print_results=True)
