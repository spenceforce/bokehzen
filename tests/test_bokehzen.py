import operator

import pytest
from bokehzen import ColumnDataSource, figure
from bokehzen.models import CDSColumn
from bokeh.models import CDSView, IndexFilter, IntersectionFilter
from bokeh.plotting.glyph_api import GlyphAPI


def test_zen_column():
    source = ColumnDataSource({"a": [1, 2], "b": [3, 4]})
    assert isinstance(source["a"], CDSColumn)
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
        (CDSColumn.isin, [1, 3], IndexFilter([0, 2])),
    ],
)
def test_static_filter(op, other, expected):
    source = ColumnDataSource({"a": [1, 2, 3]})
    assert op(source["a"], other).indices == expected.indices


def test_source_has_filter():
    source = ColumnDataSource({"a": [1, 2, 3]})
    filtered = source[source["a"] > 2]
    assert filtered.view.filter.indices == IndexFilter([2]).indices
    for attr, value in source.properties_with_values().items():
        filtered_value = getattr(filtered, attr)
        if attr == "view":
            assert value is not filtered_value and value != filtered_value
        else:
            assert value is filtered_value or value == filtered_value


def test_source_has_intersection_filter():
    source = ColumnDataSource({"a": [1, 2, 3]})
    filtered = source[source["a"] > 1]
    filtered2 = filtered[filtered["a"] < 3]
    assert filtered.view.filter in filtered2.view.filter.operands
    for indices in ([0, 1], [1, 2]):
        assert any(
            op.indices == IndexFilter(indices).indices
            for op in filtered2.view.filter.operands
        )
    assert isinstance(filtered2.view.filter, IntersectionFilter)


def test_renderer_has_view():
    x = [1, 2, 3]
    source = ColumnDataSource({"x": x, "y": x})
    filtered = source[source["x"] > 2]
    fig = figure()
    renderer = fig.scatter(x="x", y="y", source=filtered)
    assert renderer.view is filtered.view


def test_renderer_combines_views():
    x = [1, 2, 3]
    source = ColumnDataSource({"x": x, "y": x})
    filtered = source[source["x"] > 1]
    fig = figure()
    renderer = fig.scatter(
        x="x", y="y", source=filtered, view=CDSView(filter=IndexFilter([2]))
    )
    assert filtered.view.filter in renderer.view.filter.operands
    assert isinstance(renderer.view.filter, IntersectionFilter)


def test_renderer_method_metadata():
    assert GlyphAPI.line.__name__ == figure.line.__name__
    assert GlyphAPI.line.__doc__ == figure.line.__doc__
    assert GlyphAPI.line.__signature__ == figure.line.__signature__
