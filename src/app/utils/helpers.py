import json
import linecache
import tracemalloc
from src.app.config import Config


def load_json(filename: str) -> dict:
    with open(Config.JSON_DIR, filename, "r") as f:
        return json.load(f)


def save_json(filename: str, data: dict):
    with open(Config.JSON_DIR, filename, "w") as f:
        json.dump(data, f, indent=4)


def display_top(snapshot, key_type="traceback", limit=10):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    print("Top displayed")
    with open("/home/etlas/memory_usage.log", "a") as f:
        print("Top %s tracebacks" % limit, file=f)
        for index, stat in enumerate(top_stats[:limit], 1):
            print("#%s: %.1f KiB" % (index, stat.size / 1024), file=f)
            for frame in stat.traceback:
                line = linecache.getline(frame.filename, frame.lineno).strip()
                print(
                    '    File "%s", line %s, in %s' %
                    (frame.filename, frame.lineno, line),
                    file=f,
                )
            print("\n", file=f)

        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            print("%s other: %.1f KiB" % (len(other), size / 1024), file=f)
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024), file=f)
