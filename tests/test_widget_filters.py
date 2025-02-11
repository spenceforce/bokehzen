import operator

import pytest
from bokehzen import ColumnDataSource
from bokehzen.cdscolumn import CDSColumn
from bokeh.models import widgets

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


@pytest.mark.parametrize(
    "Multi", [widgets.MultiChoice, widgets.MultiSelect]
)
def test_multichoice_filter(Multi):
    values = ["A", "B", "C"]
    idx = 1
    multichoice = Multi(value=values[idx : idx + 1], options=values)
    source = ColumnDataSource({"x": values})
    index_filter = source["x"].isin(multichoice)

    assert index_filter.indices == [idx]
    assert len(multichoice.js_property_callbacks) > 0

    with pytest.raises(ValueError):
        source["x"] == multichoice


@pytest.mark.parametrize("op,expected", [(operator.lt, [0]), (operator.le, [0, 1]), (operator.eq, [1]), (operator.ne, [0, 2]), (operator.ge, [1, 2]), (operator.gt, [2]), (CDSColumn.isin, [])])
def test_numericinput_filter(op, expected):
    values = list(range(3))
    numeric = widgets.NumericInput(value=1)
    source = ColumnDataSource({"x": values})
    if op is CDSColumn.isin:
        with pytest.raises(ValueError):
            op(source["x"], numeric)
    else:
        index_filter = op(source["x"], numeric)
        assert index_filter.indices == expected
        assert len(numeric.js_property_callbacks) > 0
