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
        required=False,
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
        from .eq_query_rec.main import eq_query_rec

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
        pass
    elif args.command == "filter":
        pass
    elif args.command == "genimg":
        pass
    elif args.command == "merge":
        pass
    elif args.command == "split":
        pass
