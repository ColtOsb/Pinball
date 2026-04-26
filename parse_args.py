import argparse

def SetupParser():
    parser = argparse.ArgumentParser(
            description="Program for having the pinball machine play itself."
            )
    
    # ----- Basic arguments -----

    parser.add_argument(
            "-v"
            "--version",
            action="version",
            version="%(prog)s 0.1"
            )

    # Output level
    output_config = argparse.ArgumentParser(add_help=False)
    output_config.add_argument(
            "--verbose",
            "-v",
            action="count",
            default=0,
            help="Increases output by one level. May be used multiple times."
            )

    output_config.add_argument(
            "--quiet",
            "-q",
            action="count",
            default=0,
            help="Reduces output by one level. May be used multiple times."
            )

    # ----- Configuration arguments -----
    torch_config = argparse.ArgumentParser(add_help=False)
    torch_config.add_argument(
            "-d",
            "--device-id",
            help="The GPU device to use for inference. This is passed directly to YOLO and eventually pytorch."
            )

    plc_config = argparse.ArgumentParser(add_help=False)
    plc_config.add_argument(
            "-i",
            "--ip-address",
            help="IP address to use for the PLC connection."
            )
    plc_config.add_argument(
            "-p",
            "--port-number",
            help="Port number to use for the PLC connection."
            )

    # ----- Mode arguments -----
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("test-torch", parents=[output_config,torch_config])
    subparsers.add_parser("test-plc", parents=[output_config,plc_config])
    subparsers.add_parser("run", parents=[output_config,torch_config])


    return parser

def Setup():
    # Parse all of the args
    parser = SetupParser()
    args = parser.parse_args()

    # Go through and set them up
    args = vars(args)
    mode = args.get("command")

    # Consolidates quiet and verbose for the modes that have them.
    if mode == "run" or mode == "test-torch" or mode == "test-plc":
        verbose = args.get("verbose",0)
        quiet = args.get("quiet",0)
        output_level = verbose - quiet
        args |= {"output_level": output_level}
        args.pop("verbose")
        args.pop("quiet")

    # Default output level for modes that do not have the option to specify it.
    else:
        args |= {"output_level": 0}

    if args["output_level"] > 0:
        print(args)

    return args
