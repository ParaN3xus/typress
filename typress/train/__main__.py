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
        "--model",
        "-m",
        type=str,
        help="Path to an existing model or to save the model",
        required=True,
    )
    train_parser.add_argument(
        "--config",
        type=str,
        help="Path to the train config",
        required=True,
    )

    # tokenizer arguments
    tokenizer_parser.add_argument(
        "--dataset",
        "-d",
        type=str,
        help="Path to the dataset",
        required=True,
    )
    tokenizer_parser.add_argument(
        "--vocab_size",
        "-v",
        type=str,
        help="Path to the dataset",
        required=True,
    )

    args = parser.parse_args()

    if args.command == "train":
        from train.train import cli_train

        cli_train(args.config)
    elif args.command == "tokenizer":
        from train.train_tokenizer import train_tokenizer

        train_tokenizer(args.dataset, args.vocab_size)
