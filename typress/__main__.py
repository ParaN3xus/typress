import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="typress", description="Typst Mathematical Expression OCR"
    )

    subparsers = parser.add_subparsers(dest="command")
    parser.set_defaults(command="web")

    parser.add_argument(
        "-m",
        "--model",
        dest="model",
        type=str,
        help="Path to the model folder",
        default="paran3xus/typst_eq_ocr",
    )

    parser.add_argument(
        "-d",
        "--device",
        dest="device",
        type=str,
        help="Device to run the model",
        default="auto",
    )

    web_parser = subparsers.add_parser("web", description="Run api server")

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
        type=bool,
        help="Whether to predict continuously",
        default=True,
    )

    args = parser.parse_args()

    if args.command == "web":
        from .app.api import run_api

        web_args = web_parser.parse_args()
        run_api(args.model, args.device, web_args.host, web_args.port)
    if args.command == "cli":
        from .app.model import generate_cli

        cli_args = cli_parser.parse_args()
        generate_cli(args.model, cli_args.image, cli_args.continuous, args.device)
