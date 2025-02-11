import operator

import pytest
from bokehzen import ColumnDataSource
from bokehzen.cdscolumn import CDSColumn
from bokeh.models import IntersectionFilter, widgets


def test_zen_column():
    source = ColumnDataSource({"x": [1, 2], "y": [3, 4]})
    assert isinstance(source["x"], CDSColumn)
    assert source["x"].data == source.data["x"]
    assert source["x"].data != source["y"].data


@pytest.mark.parametrize(
    "op,other,expected",
    [
        (operator.lt, 2, [0]),
        (operator.le, 2, [0, 1]),
        (operator.eq, 2, [1]),
        (operator.ne, 2, [0, 2]),
        (operator.ge, 2, [1, 2]),
        (operator.gt, 2, [2]),
        # `operator.contains` would test if `other` is in the column. We want the opposite so
        # use `ZenColumn.isin`.
        (CDSColumn.isin, [1, 3], [0, 2]),
    ],
)
def test_static_filter(op, other, expected):
    source = ColumnDataSource({"x": [1, 2, 3]})
    assert op(source["x"], other).indices == expected


def test_source_has_filter():
    source = ColumnDataSource({"x": [1, 2, 3]})
    filtered = source[source["x"] > 2]
    assert filtered.view.filter.indices == [2]
    for attr, value in source.properties_with_values().items():
        filtered_value = getattr(filtered, attr)
        if attr == "view":
            assert value is not filtered_value and value != filtered_value
        else:
            assert value is filtered_value or value == filtered_value


def test_source_has_intersection_filter():
    source = ColumnDataSource({"x": [1, 2, 3]})
    filtered = source[source["x"] > 1]
    filtered2 = filtered[filtered["x"] < 3]
    assert filtered.view.filter in filtered2.view.filter.operands
    for indices in ([0, 1], [1, 2]):
        assert any(op.indices == indices for op in filtered2.view.filter.operands)
    assert isinstance(filtered2.view.filter, IntersectionFilter)
