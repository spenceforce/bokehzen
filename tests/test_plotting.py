import operator

import pytest
from bokehzen import ColumnDataSource, figure
from bokeh.models import CDSView, IndexFilter
from bokeh.plotting.glyph_api import GlyphAPI


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
    other_view = CDSView(filter=IndexFilter([2]))
    fig = figure()
    renderer = fig.scatter(
        x="x", y="y", source=filtered, view=other_view
    )
    assert filtered.view.filter in renderer.view.filter.operands
    assert other_view.filter in renderer.view.filter.operands
    assert len([filtered.view, other_view]) == len(renderer.view.filter.operands)


def test_renderer_method_metadata():
    assert GlyphAPI.line.__name__ == figure.line.__name__
    assert GlyphAPI.line.__doc__ == figure.line.__doc__
    assert GlyphAPI.line.__signature__ == figure.line.__signature__
