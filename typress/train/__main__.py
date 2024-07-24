import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="typress train", description="Typst Mathematical Expression OCR"
    )

    subparsers = parser.add_subparsers(dest="command")
    train_parser = subparsers.add_parser(
        "train",
        description="Train a model",
    )
    tokenizer_parser = subparsers.add_parser(
        "tokenizer", description="Train a tokenizer on a given dataset"
    )

    # train arguments
    train_parser.add_argument(
        "--config",
        "-c",
        dest="config",
        type=str,
        help="Path to the train config",
        required=True,
    )

    # tokenizer arguments
    tokenizer_parser.add_argument(
        "--csv",
        "-c",
        dest="csv",
        type=str,
        help="Path to the csv file",
        required=True,
    )
    tokenizer_parser.add_argument(
        "--vocab_size",
        "-v",
        dest="vocab_size",
        type=int,
        help="Vocab size",
        required=True,
    )

    args = parser.parse_args()

    if args.command == "train":
        from .train import cli_train

        cli_train(args.config)
    elif args.command == "tokenizer":
        from .train_tokenizer import train_tokenizer

        train_tokenizer(args.csv, args.vocab_size)
