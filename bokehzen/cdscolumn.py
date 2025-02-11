import operator

from bokeh.models import IndexFilter, Widget, widgets

from ._comparison import isin
from ._widget_filter import checkbox_filter, dropdown_filter, multioption_filter, numericinput_filter


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

    def _filter(self, op, other):
        if isinstance(other, Widget):
            return self._widget_filter(op, other)
        return self._static_filter(op, other)

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

    def _widget_filter(self, op, widget):
        if isinstance(widget, (widgets.CheckboxButtonGroup, widgets.CheckboxGroup)):
            if op is not isin:
                raise ValueError(
                    f"Only `isin` comparison is supported for `type(widget)`."
                )
            index_filter = self._static_filter(
                op, [widget.labels[i] for i in widget.active]
            )
            return checkbox_filter(widget, self.source, self.key, index_filter)

        if isinstance(widget, widgets.Dropdown):
            index_filter = IndexFilter(list(range(len(self.data))))
            return dropdown_filter(widget, self.source, self.key, index_filter, op)

        if isinstance(widget, (widgets.MultiChoice, widgets.MultiSelect)):
            if op is not isin:
                raise ValueError(
                    f"Only `isin` comparison is supported for `type(widget)`."
                )
            index_filter = self._static_filter(op, widget.value)
            return multioption_filter(widget, self.source, self.key, index_filter)

        if isinstance(widget, widgets.NumericInput):
            if op is isin:
                raise ValueError(f"`isin` comparison is not supported for `type(widget)`.")
            index_filter = self._static_filter(op, widget.value)
            return numericinput_filter(widget, self.source, self.key, index_filter, op)

    # Define operator overloads for intuitive filtering
    def __lt__(self, other):
        return self._filter(operator.lt, other)

    def __le__(self, other):
        return self._filter(operator.le, other)

    def __eq__(self, other):
        return self._filter(operator.eq, other)

    def __ne__(self, other):
        return self._filter(operator.ne, other)

    def __ge__(self, other):
        return self._filter(operator.ge, other)

    def __gt__(self, other):
        return self._filter(operator.gt, other)

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
        return self._filter(isin, other)
