import csv
import os
import random


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


def split_csv(csv_file, test_size):
    if not (0 < test_size < 1):
        raise ValueError("test_size should be a float between 0 and 1")

    csv_name = os.path.splitext(os.path.basename(csv_file))[0]
    train_filename = f"{csv_name}_train.csv"
    test_filename = f"{csv_name}_test.csv"

    csv_dir = os.path.dirname(csv_file)

    train_filepath = os.path.join(csv_dir, train_filename)
    test_filepath = os.path.join(csv_dir, test_filename)

    with open(csv_file, mode="r", newline="") as file:
        reader = csv.reader(file)
        header = next(reader)

        rows = list(reader)

        random.shuffle(rows)

        test_size_count = int(len(rows) * test_size)

        test_rows = rows[:test_size_count]
        train_rows = rows[test_size_count:]

    with open(train_filepath, mode="w", newline="") as train_file:
        writer = csv.writer(train_file)
        writer.writerow(header)
        writer.writerows(train_rows)

    with open(test_filepath, mode="w", newline="") as test_file:
        writer = csv.writer(test_file)
        writer.writerow(header)
        writer.writerows(test_rows)

    print(f"Train file saved as: {train_filepath}")
    print(f"Test file saved as: {test_filepath}")
