"""
Utility class for printing lists of lists, lists of dicts and lists of dataclasses
"""

from typing import Any
import dataclasses


def print_lists(rows: list[list[Any]], header: bool = False) -> str:
    widths = [0] * len(rows[0])
    for row in rows:
        for i, col in enumerate(row):
            widths[i] = max(len(str(col)), widths[i])
    result = []
    for row in rows:
        pretty_row = []
        for i, col in enumerate(row):
            x = str(col).rjust(widths[i])
            pretty_row.append(x)
        result.append(" | ".join(pretty_row))

    if header:
        sep = "-" * len(result[0])
        result.insert(1, sep)

    return "\n".join(result)


def print_dicts(rows: list[dict]) -> str:
    lists = [list(rows[0].keys())]
    lists.extend(list(x.values()) for x in rows)
    return print_lists(lists, header=True)


def print_dataclasses(dcs: list[Any]) -> str:
    dicted = [dataclasses.asdict(d) for d in dcs]
    return print_dicts(dicted)
