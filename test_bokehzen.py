import operator

import pytest
from bokehzen import ColumnDataSource, ZenColumn
from bokeh.models import IndexFilter


def test_zen_column():
    source = ColumnDataSource({"a": [1, 2], "b": [3, 4]})
    assert isinstance(source["a"], ZenColumn)
    assert source["a"].data == source.data["a"]
    assert source["a"].data != source["b"].data


@pytest.mark.parametrize(
    "op,other,expected",
    [
        (operator.lt, 2, IndexFilter([0])),
        (operator.le, 2, IndexFilter([0, 1])),
        (operator.eq, 2, IndexFilter([1])),
        (operator.ne, 2, IndexFilter([0, 2])),
        (operator.ge, 2, IndexFilter([1, 2])),
        (operator.gt, 2, IndexFilter([2])),
        # `operator.contains` would test if `other` is in the column. We want the opposite so
        # use `ZenColumn.isin`.
        (ZenColumn.isin, [1, 3], IndexFilter([0, 2]))
    ]
)
def test_static_filter(op, other, expected):
    source = ColumnDataSource({"a": [1, 2, 3]})
    assert op(source["a"], other).indices == expected.indices
