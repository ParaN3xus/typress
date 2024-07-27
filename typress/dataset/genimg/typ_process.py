class Processor:
    """
    A + B = x => B(A(x))
    """

    def __init__(self, f) -> None:
        self.process = f

    def __add__(self, other):
        return Processor(lambda x: other.process(self.process(x)))

    def __call__(self, x):
        return self.process(x)

    @property
    def copy(self):
        return Processor(self.process)


ALL = Processor(lambda x: x)


def processor(parent=ALL):
    def f(g):
        if parent is not None and isinstance(parent, Processor):
            c = parent.copy
            parent.process = (lambda x: g(c(x)))
        return Processor(g)
    return f


@processor()
def remove_return(x):
    return x.replace('\r', '')


@processor()
def no_hashtag(x):
    assert "#" not in x
    return x


@processor()
def process_qty(x):
    def qty_to_typ(num: str, unit: str) -> str:
        def num_to_typ(num: str) -> str:
            num = num.lower()
            if "e" in num:
                f, e = num.split("e")
                return f"{f} times 10^({e})"
            return num

        def unit_to_typ(unit: str) -> str:
            if "/" in unit:
                n, d = unit.split("/")
                return f"{unit_to_typ(n)} slash {unit_to_typ(d)}"
            return " ".join(map(
                lambda x: f"upright({' '.join(x)})",
                unit.split(" ")
            ))
        return f"{num_to_typ(num)} med {unit_to_typ(unit)}"

    import re
    return re.sub(
        r'qty\("([^"]*)", "([^"]*)"\)',
        lambda m: qty_to_typ(m.group(1), m.group(2)),
        x
    )


@processor()
def standardize(x):
    import re
    # remove multiple spaces
    x = re.sub(
        r"\s+",
        " ",
        x
    )
    return x


if __name__ == "__main__":
    # print(
    #     ALL(
    #         r"""qty("1.0e-3", "m/s")"""
    #     )
    # )

    def find_equations(content: str) -> list[str]:
        import re
        return re.findall(
            r'(?<!\\)(\$.*?\$)(?<!\\)',
            content
        )

    equations = set()

    # walk in current directory find .typ files
    import os
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".typ"):
                with open(
                    os.path.join(root, file), "r", encoding="utf-8"
                ) as f:
                    content = f.read()
                    eqs = []
                    for eq in find_equations(content):
                        try:
                            eqs.append(ALL(eq))
                        except:
                            pass
                    equations.update(eqs)

    import json

    with open("equations.json", "w") as f:
        json.dump(
            list(equations),
            f
        )
