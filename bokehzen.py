"""BokehZen"""
import inspect
import operator

from bokeh.models import ColumnDataSource as BokehColumnDataSource, CDSView, Filter, IndexFilter
from bokeh.plotting import figure as BokehFigure
from bokeh.plotting.glyph_api import GlyphAPI


# class ZenDataSource:

#     def __init__(self, source, view=None):
#         self.source = source
#         self.view = view

#     def __getattr__(self, attr):
#         return getattr(self.source, attr)

#     def __getitem__(self, item):
#         x = self.source[item]
#         cls = type(self)
#         if isinstance(x, cls):
#             return cls(x.source, CDSView(filter=self.view.filter & x.filter))
#         return x

def _reverse_contains(x, y):
    return operator.contains(y, x)

class ZenColumn:

    def __init__(self, source, key):
        self.source = source
        self.key = key

    @property
    def data(self):
        return self.source.data[self.key]

    def _static_filter(self, op, other):
        return IndexFilter([i for i, x in enumerate(self.data) if op(x, other)])

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
        return self._static_filter(_reverse_contains, other)


class ColumnDataSource(BokehColumnDataSource):

    def __getitem__(self, item):
        if isinstance(item, str):
            return ZenColumn(self, item)
        if isinstance(item, Filter):
            return ZenDataSource(self, view=CDSView(filter=item))
        raise TypeError(f"Expects type `str` or `Filter`. Got {type(item)}.")

    
# class figure(BokehFigure): pass


# def update_renderer(attr, prop):
#     def func(*args, **kwargs):
#         if "source" in kwargs and "view" not in kwargs:
#             try:
#                 kwargs["view"] = source.view
#             except AttributeError:
#                 pass
#         return prop(*args, **kwargs)
#     func.__signature__ = prop.__signature__
#     func.__name__ = prop.__name__
#     func.__doc__ = prop.__doc__
#     setattr(figure, attr, func)


# for attr, prop in inspect.getmembers(GlyphAPI):
#     if (callable(prop) and not attr.startswith("_")) or attr == "_scatter":
#         update_renderer(attr, prop)
        
