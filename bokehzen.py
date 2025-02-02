"""BokehZen: A Simplified API for Bokeh

This module extends Bokeh to provide an intuitive way to filter ColumnDataSource
using operators without requiring explicit callbacks.
"""
import operator
from functools import wraps
from inspect import getmembers, signature

from bokeh import __version__ as __bk_version__
from bokeh.core.properties import Instance, Nullable
from bokeh.model import DataModel
from bokeh.models import (
    CDSView,
    ColumnDataSource as BokehColumnDataSource,
    Filter,
    IndexFilter,
)
from bokeh.plotting import figure as BokehFigure
from bokeh.plotting._renderer import GlyphRenderer
from bokeh.plotting.glyph_api import GlyphAPI

__all__ = ["ColumnDataSource", "figure"]

# Extract Bokeh version as a list of integers
_bk_version = [int(x) for x in __bk_version__.split(".")]

# Define available glyph methods based on Bokeh version
if _bk_version[0] == 3 and _bk_version[1] <= 6:
    # Explicitly list glyph methods for older Bokeh versions
    glyph_methods = [
        "annular_wedge",
        "annulus",
        "arc",
        "asterisk",
        "bezier",
        "circle",
        "block",
        "circle_cross",
        "circle_dot",
        "circle_x",
        "circle_y",
        "cross",
        "dash",
        "diamond",
        "diamond_cross",
        "diamond_dot",
        "dot",
        "harea",
        "harea_step",
        "hbar",
        "hspan",
        "hstrip",
        "ellipse",
        "hex",
        "hex_dot",
        "hex_tile",
        "image",
        "image_rgba",
        "image_stack",
        "image_url",
        "inverted_triangle",
        "line",
        "mathml",
        "multi_line",
        "multi_polygons",
        "ngon",
        "patch",
        "patches",
        "plus",
        "quad",
        "quadratic",
        "ray",
        "rect",
        "step",
        "segment",
        "square",
        "square_cross",
        "square_dot",
        "square_pin",
        "square_x",
        "star",
        "star_dot",
        "tex",
        "text",
        "triangle",
        "triangle_dot",
        "triangle_pin",
        "varea",
        "varea_step",
        "vbar",
        "vspan",
        "vstrip",
        "wedge",
        "x",
        "y",
        "scatter",
    ]
    for gm in glyph_methods:
        assert hasattr(GlyphAPI, gm)
else:
    # Dynamically extract available glyph methods for newer Bokeh versions
    glyph_methods = [
        name
        for name, prop in getmembers(GlyphAPI)
        if signature(prop).return_annotation is GlyphRenderer
    ]


def _reverse_contains(x, y):
    """
    Helper function to reverse the order of arguments for `in` operations.

    Parameters
    ----------
    x : Any
        The item to check for containment.
    y : Any
        The collection to check within.

    Returns
    -------
    bool
        True if `x` is in `y`, False otherwise.
    """
    return operator.contains(y, x)


class CDSColumn:
    """Wrapper for a column in a ColumnDataSource, enabling operator-based filtering."""

    def __init__(self, source, key):
        """
        Initialize CDSColumn with a reference to the ColumnDataSource and the column key.

        Parameters
        ----------
        source : ColumnDataSource
            The data source containing the column.
        key : str
            The name of the column.
        """
        self.source = source
        self.key = key

    @property
    def data(self):
        """
        Retrieve the column data from the source.

        Returns
        -------
        list
            The data contained in the specified column.
        """
        return self.source.data[self.key]

    def _static_filter(self, op, other):
        """
        Apply a static filter to the column using the given operator.

        Parameters
        ----------
        op : function
            The comparison operator function.
        other : Any
            The value to compare against.

        Returns
        -------
        IndexFilter
            A filter object with indices where the condition is met.
        """
        return IndexFilter([i for i, x in enumerate(self.data) if op(x, other)])

    # Define operator overloads for intuitive filtering
    def __lt__(self, other):
        return self._static_filter(operator.lt, other)

    def __le__(self, other):
        return self._static_filter(operator.le, other)

    def __eq__(self, other):
        return self._static_filter(operator.eq, other)

    def __ne__(self, other):
        return self._static_filter(operator.ne, other)

    def __ge__(self, other):
        return self._static_filter(operator.ge, other)

    def __gt__(self, other):
        return self._static_filter(operator.gt, other)

    def isin(self, other):
        """
        Check if elements in the column belong to the given collection.

        Parameters
        ----------
        other : iterable
            The collection of values to check membership against.

        Returns
        -------
        IndexFilter
            A filter object indicating which indices satisfy the condition.
        """
        return self._static_filter(_reverse_contains, other)


class ColumnDataSource(BokehColumnDataSource, DataModel):
    """Enhanced ColumnDataSource that supports direct filtering with operators."""

    view = Nullable(Instance(CDSView), help="An optional view for filtering data.")

    def __getitem__(self, item):
        """
        Enable column access and filtering through the bracket operator.

        Parameters
        ----------
        item : str or Filter
            The column key or a filter object.

        Returns
        -------
        CDSColumn or ColumnDataSource
            A wrapped column or filtered data source.
        """
        if isinstance(item, str):
            return CDSColumn(self, item)  # Return column wrapper
        if isinstance(item, Filter):
            if self.view is None:
                return self.clone(view=CDSView(filter=item))  # Apply filter
            else:
                return self.clone(view=CDSView(filter=self.view.filter & item))
        raise TypeError(f"Expected type `str` or `Filter`. Got {type(item)}.")


class figure(BokehFigure, DataModel):
    """Custom figure class that integrates automatic filtering with glyph methods."""

    pass


def _wrap_glyph_method(f):
    """
    Wrapper for glyph methods to automatically apply filtering if available.

    Parameters
    ----------
    f : function
        The original glyph method.

    Returns
    -------
    function
        The wrapped function that applies filtering if available.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "source" in kwargs and hasattr(kwargs["source"], "view"):
            view = kwargs["source"].view
            if "view" in kwargs:
                kwargs["view"] = CDSView(filter=kwargs["view"].filter & view.filter)
            else:
                kwargs["view"] = view
        return f(*args, **kwargs)

    return wrapper


# Apply the glyph method wrapper to all available glyphs
for glyph_method in glyph_methods:
    setattr(figure, glyph_method, _wrap_glyph_method(getattr(figure, glyph_method)))
