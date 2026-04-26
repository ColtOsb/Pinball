import parse_args

def Main():
    args = parse_args.Setup()
    mode = args["command"]
    if not mode:
        print("Invalid mode selected.")
        exit(1)

    elif mode == "run":
        pass

    elif mode == "test-torch":
        device_id = args.get("device_id")
        
        function_args = {"print_results": True}
        if device_id is not None:
            function_args |= {"device_id": device_id}

        from environments.test_torch.run import TorchTest
        TorchTest.Test(**function_args)


if __name__ == "__main__":
    Main()
