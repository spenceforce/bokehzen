import operator as op

import pytest
from bokehzen import ColumnDataSource, ZenColumn
from bokeh.models import IndexFilter


def test_zen_column():
    source = ColumnDataSource({"a": [1, 2], "b": [3, 4]})
    assert isinstance(source["a"], ZenColumn)
    assert source["a"].data == source.data["a"]
    assert source["a"].data != source["b"].data


@pytest.mark.parametrize(
    "operator,other,expected",
    [
        (op.lt, 2, IndexFilter([0])),
        (op.le, 2, IndexFilter([0, 1])),
        (op.eq, 2, IndexFilter([1])),
        (op.ne, 2, IndexFilter([0, 2])),
        (op.ge, 2, IndexFilter([1, 2])),
        (op.gt, 2, IndexFilter([2])),
        (op.contains, [1, 3], IndexFilter([0, 2]))
    ]
)
def test_static_filter(operator, other, expected):
    source = ColumnDataSource({"a": [1, 2, 3]})
    if operator is not op.contains:
        assert operator(source["a"], other).indices == expected.indices
    else:
        assert source["a"].isin(other).indices == expected.indices
