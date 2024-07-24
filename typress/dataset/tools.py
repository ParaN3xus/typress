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
