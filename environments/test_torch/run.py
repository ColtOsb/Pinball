class TorchTest:
    torch = None

    def PrintResults(results):
        if not isinstance(results,list):
            results = [results]

        for name, status, output in results:
            print(f"-----Test: {name} ... {'Success' if status else 'Fail'}-----",end="")
            if not output:
                print()
            else:
                print(" Output: ",end="")
                if len(str(output).splitlines()) > 1:
                    print()

                print(output)
            

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

    def Test(device_id=0, print_results=False, return_results=True):
        results = []

        tests = [
                 ("Importing torch",TorchTest.TestImportTorch,[]),
                 ("CUDA/GPU Available",TorchTest.TestGPUAvailable,[]),
                 ("Device Name",TorchTest.TestDeviceName,[device_id]),
                 ("Torch Env",TorchTest.TestTorchEnv,[])
                 ]

        for name,test,args in tests:
            result = None
            try:
                output = test(*args)
                result = (name,True,output)
            except Exception as e:
                result = (name,False,e)

            results.append(result)
            if print_results:
                TorchTest.PrintResults(result)

        if return_results:
            return results


if __name__ == "__main__":
    results = TorchTest.Test(print_results=True)
