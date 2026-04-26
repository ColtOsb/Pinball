import parse_args

def Main():
    args = parse_args.Setup()
    mode = args["command"]

    # Somehow a mode was not specified. Should not be possible
    # with argparse parsing.
    if not mode:
        print("Invalid mode selected.")
        exit(1)

    # Run the ai on the game
    elif mode == "run":
        import ai_yolo
        ai_yolo.Main(args.get("output_level",0))

    # Perform tests on the pytorch environment
    elif mode == "test-torch":
        device_id = args.get("device_id")
        
        function_args = {"print_results": True, "output_level": args.get("output_level",0)}
        if device_id is not None:
            function_args |= {"device_id": device_id}

        from testcases.test_torch import TorchTest
        TorchTest.Test(**function_args)

    # Perform tests on the plc connection
    elif mode == "test-plc":
        ip_address = args.get("ip_address")
        port = args.get("port_number")
        
        function_args = {"print_results": True, "output_level": args.get("output_level",0)}
        for item in [("ip_address",ip_address),("port",port)]:
            name, val = item
            if val is not None:
                function_args |= {name: val}

        from testcases.test_plc import PLCTest
        PLCTest.Test(**function_args)


if __name__ == "__main__":
    Main()
