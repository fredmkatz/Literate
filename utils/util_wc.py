import os
from utils.util_fmk import glob_files


def wc(filenames):
    results = {}
    for filename in filenames:
        chars = 0
        words = 0
        lines = 0
        try:
            with open(filename, "r", encoding="utf-8") as fh:
                for line in fh:
                    lines += 1
                    words += len(line.split())
                    chars += len(line)
            results[filename] = {
                "lines": lines,
                "words": words,
                "chars": chars,
            }
        except Exception as err:
            print(err)
    return results


def word_count(*patterns):
    print(f"patterns are {patterns}")
    files = glob_files(*patterns)
    results = wc(files)
    totals = {
        "lines": 0,
        "words": 0,
        "chars": 0,
    }
    for filename in files:
        res = results[filename]
        basename = os.path.basename(filename)
        print(
            "{} {} {}\t\t{}".format(res["lines"], res["words"], res["chars"], basename)
        )
        for k in res:
            totals[k] += res[k]
    print(
        "{} {} {} {}".format(totals["lines"], totals["words"], totals["chars"], "total")
    )


if __name__ == "__main__":
    word_count("grammars/Markdown/Markdown_outputs/*")
