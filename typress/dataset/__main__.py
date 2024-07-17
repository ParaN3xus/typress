import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Typress Dataset Tools",
        description="Tools for preprocessing Typress dataset",
    )

    subparsers = parser.add_subparsers(dest="command")

    normalize_parser = subparsers.add_parser(
        "extract", description="Extract formulas from Typst workspace"
    )

    convert_parser = subparsers.add_parser(
        "convert", description="Convert LaTeX formulas to Typst formulas"
    )

    normalize_parser = subparsers.add_parser(
        "normalize", description="Normalize formulas"
    )

    filter_parser = subparsers.add_parser(
        "filter", description="Filter invalid formulas"
    )

    genimg_parser = subparsers.add_parser(
        "genimg", description="Generate image for formulas"
    )

    merge_parser = subparsers.add_parser(
        "merge", description="Merge two datasets into one"
    )

    split_parser = subparsers.add_parser(
        "split", description="Split dataset to train and test"
    )

    args = parser.parse_args()

    if args.command == "extract":
        pass
    elif args.command == "convert":
        pass
    elif args.command == "normalize":
        pass
    elif args.command == "filter":
        pass
    elif args.command == "genimg":
        pass
    elif args.command == "merge":
        pass
    elif args.command == "split":
        pass
