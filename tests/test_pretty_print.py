from dataclasses import dataclass
from colmi_r02_client.pretty_print import print_lists, print_dicts, print_dataclasses


@dataclass
class FooBar:
    foo: str
    bar: int


def test_print_lists_simple():
    lists = ["aaa", "b"], ["c", "dd"]

    expected = "aaa |  b\n  c | dd"
    actual = print_lists(lists)
    assert actual == expected


def test_print_lists_header():
    lists = ["aaa", "b"], ["c", "dd"]

    expected = "aaa |  b\n--------\n  c | dd"
    actual = print_lists(lists, header=True)
    assert actual == expected


def test_print_dicts():
    dicts = [{"a": 1, "b": 1000}, {"a": 2, "b": 3}]

    expected = "a |    b\n--------\n1 | 1000\n2 |    3"
    actual = print_dicts(dicts)
    assert actual == expected


def test_print_dataclasses():
    dcs = [FooBar("a", 1), FooBar("aaaaaa", 10000)]

    expected = "   foo |   bar\n--------------\n     a |     1\naaaaaa | 10000"
    actual = print_dataclasses(dcs)
    assert actual == expected


# TODO add some nice juicy property tests
