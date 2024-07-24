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

    convert_parser.add_argument(
        "-c",
        "--csv",
        dest="filename",
        type=str,
        help="csv file to process",
        required=True,
    )

    normalize_parser = subparsers.add_parser(
        "normalize", description="Normalize formulas"
    )

    normalize_parser.add_argument(
        "-c",
        "--csv",
        dest="filename",
        type=str,
        help="csv file to process",
        required=True,
    )

    filter_parser = subparsers.add_parser("filter", description="Filter empty formulas")

    filter_parser.add_argument(
        "-c",
        "--csv",
        dest="filename",
        type=str,
        help="csv file to process",
        required=True,
    )

    genimg_parser = subparsers.add_parser(
        "genimg", description="Generate image for formulas"
    )

    genimg_parser.add_argument(
        "-j",
        "--json",
        dest="filename",
        type=str,
        help="json file to process",
        required=True,
    )

    merge_parser = subparsers.add_parser(
        "merge", description="Merge two datasets into one"
    )

    merge_parser.add_argument(
        "-c1",
        "--csv1",
        dest="csv1",
        type=str,
        help="first csv file to merge",
        required=True,
    )

    merge_parser.add_argument(
        "-c2",
        "--csv2",
        dest="csv2",
        type=str,
        help="second csv file to merge",
        required=True,
    )

    split_parser = subparsers.add_parser(
        "split", description="Split dataset to train and test"
    )

    split_parser.add_argument(
        "-c",
        "--csv",
        dest="csv",
        type=str,
        help="csv file to split",
        required=True,
    )

    split_parser.add_argument(
        "-s",
        "--test_size",
        dest="test_size",
        type=float,
        help="Test set size ratio",
        required=True,
    )

    args = parser.parse_args()

    if args.command == "extract":
        from .eq_query_rec.eq_query_rec import eq_query_rec

        eq_query_rec()
    elif args.command == "convert":
        import os
        import subprocess

        current_dir = os.path.dirname(__file__)
        node_script_path = os.path.join(current_dir, "tex2typ", "index.js")

        csv_file_name = args.filename
        command = ["node", node_script_path, "csv", csv_file_name]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error calling Node.js script:")
            print(e.stderr)

    elif args.command == "normalize":
        from .eq_query_rec.normalize import normalize_csv_column

        normalize_csv_column(args.filename)

    elif args.command == "filter":
        from .tools import filter_csv

        filter_csv(args.filename)
    elif args.command == "genimg":
        from .genimg import genimg

        genimg(args.filename)
    elif args.command == "merge":
        from .tools import merge_csv

        merge_csv(args.csv1, args.csv2)
    elif args.command == "split":
        from .tools import split_csv

        split_csv(args.csv, args.test_size)
