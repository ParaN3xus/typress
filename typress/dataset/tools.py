import csv
import os


def filter_csv(file_name):
    output_file_name = (
        f"{os.path.dirname(file_name)}/filtered_{os.path.basename(file_name)}"
    )

    with open(file_name, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    with open(output_file_name, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for row in rows:
            if len(row) > 1 and row[1].strip() != "":
                writer.writerow(row)


def merge_csv(csv1, csv2):
    csv1_name = os.path.splitext(os.path.basename(csv1))[0]
    csv2_name = os.path.splitext(os.path.basename(csv2))[0]
    merged_filename = f"merged_{csv1_name}_{csv2_name}.csv"

    csv1_dir = os.path.dirname(csv1)

    merged_filepath = os.path.join(csv1_dir, merged_filename)

    with open(csv1, mode="r", newline="") as file1, open(
        csv2, mode="r", newline=""
    ) as file2, open(merged_filepath, mode="w", newline="") as merged_file:
        reader1 = csv.reader(file1)
        reader2 = csv.reader(file2)
        writer = csv.writer(merged_file)

        for row in reader1:
            writer.writerow(row)

        next(reader2)

        for row in reader2:
            writer.writerow(row)

    print(f"Merged file saved as: {merged_filepath}")
