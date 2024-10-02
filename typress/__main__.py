import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="typress", description="Typst Mathematical Expression OCR"
    )

    subparsers = parser.add_subparsers(dest="command")
    parser.set_defaults(command="web")

    web_parser = subparsers.add_parser("web", description="Run api server")

    web_parser.add_argument(
        "-m",
        "--model",
        dest="model",
        type=str,
        help="Path to the model folder",
        default="paran3xus/typress_ocr",
    )

    web_parser.add_argument(
        "-d",
        "--device",
        dest="device",
        type=str,
        help="Device to run the model",
        default="auto",
    )

    web_parser.add_argument(
        "--host",
        dest="host",
        type=str,
        help="Host to listen",
        default="localhost",
    )

    web_parser.add_argument(
        "-p",
        "--port",
        dest="port",
        type=int,
        help="HTTP server port",
        default=5676,
    )

    cli_parser = subparsers.add_parser("cli", description="Run cli")

    cli_parser.add_argument(
        "-m",
        "--model",
        dest="model",
        type=str,
        help="Path to the model folder",
        default="paran3xus/typress_ocr",
    )

    cli_parser.add_argument(
        "-d",
        "--device",
        dest="device",
        type=str,
        help="Device to run the model",
        default="auto",
    )

    cli_parser.add_argument(
        "-i",
        "--image",
        dest="image",
        type=str,
        help="Image to recognize",
        required=False,
    )

    cli_parser.add_argument(
        "-c",
        "--continuous",
        dest="continuous",
        action="store_true",
        help="Whether to predict continuously",
    )

    args = parser.parse_args()

    if args.command == "web":
        from .app.api import get_app

        if not args.__contains__("host"):
            args.host = "localhost"
        if not args.__contains__("port"):
            args.port = 5676
        if not args.__contains__("model"):
            args.model = "paran3xus/typress_ocr"
        if not args.__contains__("device"):
            args.device = "auto"
        get_app(args.model, args.device, f"http://{args.host}:{args.port}").run(
            args.host, args.port, debug=True
        )
    if args.command == "cli":
        from .app.model import generate_cli

        generate_cli(args.model, args.image, args.continuous, args.device)
