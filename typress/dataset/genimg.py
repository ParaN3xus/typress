from pathlib import Path
import os
import tqdm
from .typ_process import ALL as preprocessor
import hashlib
import subprocess
import csv
import concurrent.futures
from threading import Lock

TEMP_PATH = None
IMG_PATH = None

PPI_LIST = (
    # 64,
    144,
    # 256,
)

hashes = set()
equations = set()
lock = Lock()
fail_count, all_count = 0, 0


def eqs_from_json(f, desc=None):
    import json

    with open(f) as f:
        data = json.load(f)
    for eq in tqdm.tqdm(data, total=len(data), leave=False, desc=desc):
        try:
            e = preprocessor(eq)
            e.encode("utf-8").decode("ascii")
            yield e
        except:
            continue


def gen_name(eq) -> str:
    if eq in equations:
        raise ValueError(f"Duplicate equation: {eq}")
    equations.add(eq)
    original_hash = cur_name = hashlib.md5(eq.encode("utf-8")).hexdigest()
    counter = 1
    while cur_name in hashes:
        cur_name = f"{original_hash}_{counter}"
        counter += 1
    hashes.add(cur_name)
    return cur_name


def gen_typ(eq):
    # TODO: maybe add some import? not sure
    return f"""#set page(width: auto, height: auto, margin: 6pt)\n$ {eq} $"""


def gen_img(equation: str) -> str:
    """returns the file name of the image (without the `_{ppi}` part)"""
    name = gen_name(equation)
    input_fn = TEMP_PATH / f"{name}.typ"

    def output_fn(ppi):
        return IMG_PATH / f"{name}_{ppi}.png"

    with open(input_fn, "w") as f:
        f.write(gen_typ(equation))
    ok = True
    for ppi in PPI_LIST:
        if os.path.exists(output_fn(ppi)):
            continue
        res = subprocess.run(
            ["typst", "compile", input_fn, output_fn(ppi), "--ppi", str(ppi)],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        # capture the stderr, if not empty, raise an error after unlinking the input file
        if res.stderr:
            print(res.stderr)
            ok = False
            break
    input_fn.unlink()
    if not ok:
        raise ValueError(f"Failed to compile {equation}")
    return name


def process_equation(writer, eq):
    global fail_count, all_count
    all_count += 1
    try:
        img_name = gen_img(eq)
        with lock:
            for ppi in PPI_LIST:
                writer.writerow(
                    {"image_prefix": f"{img_name}_{ppi}.png", "formula": eq}
                )
    except Exception as e:
        with lock:
            fail_count += 1
            print(e)


def genimg(json_fp):
    # Create if not exists
    root = Path(os.path.dirname(json_fp))

    global IMG_PATH
    global TEMP_PATH
    IMG_PATH = root / "img"
    TEMP_PATH = root / "tmp"

    for path in [TEMP_PATH, IMG_PATH]:
        path.mkdir(parents=True, exist_ok=True)

    csv_fp = f"{root}/dataset.csv"
    with open(csv_fp, "w", newline="") as csvfile:
        fieldnames = ["image_prefix", "formula"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        global fail_count
        global all_count

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_equation, writer, eq)
                for eq in eqs_from_json(json_fp)
            ]
            concurrent.futures.wait(futures)

    print(f"Total: {all_count}, Failed: {fail_count}")
