import operator

import pytest
from bokehzen import ColumnDataSource
from bokehzen.models import CDSColumn
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


@pytest.mark.parametrize(
    "Checkbox", [widgets.CheckboxButtonGroup, widgets.CheckboxGroup]
)
def test_checkbox_filter(Checkbox):
    values = ["A", "B", "C"]
    checkbox = Checkbox(labels=values, active=[0])
    source = ColumnDataSource({"x": values})
    index_filter = source["x"].isin(checkbox)

    assert index_filter.indices == [0]
    assert len(checkbox.js_property_callbacks) > 0

    with pytest.raises(ValueError):
        source["x"] == checkbox


def test_dropdown_filter():
    values = ["A", "B", "C"]
    dropdown = widgets.Dropdown(menu=values)
    source = ColumnDataSource({"x": values})
    index_filter = source["x"] == dropdown

    assert index_filter.indices == [0, 1, 2]
    assert len(dropdown.js_event_callbacks) > 0

    dropdown = widgets.Dropdown(menu=values)
    index_filter = source["x"].isin(dropdown)
    assert index_filter.indices == [0, 1, 2]
    assert len(dropdown.js_event_callbacks) > 0


def test_multichoice_filter():
    values = ["A", "B", "C"]
    idx = 1
    multichoice = widgets.MultiChoice(value=values[idx : idx + 1], options=values)
    source = ColumnDataSource({"x": values})
    index_filter = source["x"].isin(multichoice)

    assert index_filter.indices == [idx]
    assert len(multichoice.js_property_callbacks) > 0

    with pytest.raises(ValueError):
        source["x"] == multichoice
