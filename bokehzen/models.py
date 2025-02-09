"""
Data Models for BokehZen

This module extends Bokeh's `ColumnDataSource` to support operator-based filtering directly on data columns. It provides an enhanced `ColumnDataSource` that allows intuitive data filtering using standard Python operators.
"""

from bokeh.core.properties import Instance, Nullable
from bokeh.model import DataModel
from bokeh.models import *
from bokeh.models import __all__, ColumnDataSource as BokehColumnDataSource
from bokehzen.cdscolumn import CDSColumn


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
            return CDSColumn(self, item)
        if isinstance(item, Filter):
            if self.view is None:
                return self.clone(view=CDSView(filter=item))
            else:
                # Take the intersection of the existing and new filters.
                view = CDSView(filter=self.view.filter & item)
                return self.clone(view=view)
        raise TypeError(f"Expected type `str` or `Filter`. Got {type(item)}.")
