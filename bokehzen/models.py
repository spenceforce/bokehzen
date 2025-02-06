"""
Data Models for BokehZen

This module extends Bokeh's `ColumnDataSource` to support operator-based filtering directly on data columns. It provides an enhanced `ColumnDataSource` that allows intuitive data filtering using standard Python operators.
"""
import operator

from bokeh.core.properties import Instance, Nullable
from bokeh.model import DataModel
from bokeh.models import *
from bokeh.models import __all__, ColumnDataSource as BokehColumnDataSource


def _isin(x, y):
    """
    Check if an element exists within a collection.

    Parameters
    ----------
    x : Any
        The element to check for membership.
    y : Any
        The collection in which to check for `x`.

    Returns
    -------
    bool
        True if `x` is in `y`, otherwise False.
    """
    return x in y


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
        return self._static_filter(_isin, other)


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
