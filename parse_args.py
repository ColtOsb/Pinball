import argparse

def SetupParser():
    parser = argparse.ArgumentParser(
            description="Program for having the pinball machine play itself."
            )
    
    # ----- Basic arguments -----

    parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s 0.1"
            )

    # Output level
    parser.add_argument(
            "--verbose",
            "-v",
            action="count",
            default=0,
            help="Increases output by one level. May be used multiple times."
            )

    parser.add_argument(
            "--quiet",
            "-q",
            action="count",
            default=0,
            help="Reduces output by one level. May be used multiple times."
            )

    parser.add_argument(
            "-d",
            "--device-id",
            help="The GPU device to use for inference. This is passed directly to YOLO and eventually pytorch."
            )

    return parser

def Setup():
    # Parse all of the args
    parser = SetupParser()
    args = parser.parse_args()

    # Go through and set them up
    args = vars(args)
    verbose = args.get("verbose",0)
    quiet = args.get("quiet",0)
    output_level = verbose - quiet
    args |= {"output-level": output_level}
    args.pop("verbose")
    args.pop("quiet")
    if args["output-level"] > 0:
        print(args)

    return args
