"""
Plotting Utilities for BokehZen

This module extends Bokeh's `figure` class by integrating automatic filtering with glyph methods. It wraps Bokeh's native plotting API to allow seamless filtering using BokehZen's enhanced `ColumnDataSource`.
"""

import operator
from functools import wraps
from inspect import getmembers, signature

from bokeh import __version__ as __bk_version__
from bokeh.model import DataModel
from bokeh.plotting import *
from bokeh.plotting import __all__, figure as BokehFigure
from bokeh.plotting._renderer import GlyphRenderer
from bokeh.plotting.glyph_api import GlyphAPI

from .models import CDSView

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
else:
    # Dynamically extract available glyph methods for newer Bokeh versions
    glyph_methods = [
        name
        for name, prop in getmembers(GlyphAPI)
        if signature(prop).return_annotation is GlyphRenderer
    ]


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
