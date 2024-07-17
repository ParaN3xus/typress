import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="typress", description="Typst Mathematical Expression OCR"
    )

    parser.set_defaults(command="predict")

    parser.add_argument(
        "-m",
        "--model",
        dest="model",
        type=str,
        help="Path to the model folder",
        required=True,
    )
    parser.add_argument(
        "-i",
        "--image",
        dest="image",
        type=str,
        help="Image to recognize",
        required=False,
    )
    parser.add_argument(
        "-c",
        "--continuous",
        dest="continuous",
        type=bool,
        help="Whether to predict continuously",
        default=True,
    )
    args = parser.parse_args()

    from model.model import generate_cli

    generate_cli(args.model, args.image, args.continuous)
