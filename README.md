# BokehZen

BokehZen aims to make [Bokeh](https://bokeh.org/) more user-friendly by simplifying the developer experience. By abstracting away callbacks, BokehZen provides an intuitive API for binding widgets to plots, making it easier to build interactive visualizations without the complexity.

## Features

- **Declarative API:** A high-level approach to defining interactivity without writing low-level event handlers.
- **Minimal Boilerplate:** Reduce the need for manual callback definitions.
- **Flexible Integration:** Works with existing Bokeh projects and layouts.

## Pandas style filtering

Filtering a `ColumnDataSource` is easy in BokehZen using common comparison operators.

```python
from bokehzen import ColumnDataSource, figure
from bokeh.plotting import show

x = y = [1, 2, 3]
source = ColumnDataSource({"x": x, "y": y})
# Exclude point (1, 1)
filtered = source[source["x"] >= 2]

fig = figure()
# No need to pass the filter to `scatter`. It's handled automatically.
fig.scatter(x="x", y="y", source=filtered)
# The figure only displays points (2, 2) and (3, 3)
show(fig)
```

To make things even smoother, filters are linked to data sources so there's no need to pass them to glyph renderer methods.

## Interactive filtering

Dynamic filters with widgets are easy. No more callbacks.

```python
from bokehzen import ColumnDataSource, figure
from bokeh.layouts import layout
from bokeh.models import Slider
from bokeh.plotting import show

slider = Slider(start=1, end=4, value=1, step=1)

x = y = [1, 2, 3]
source = ColumnDataSource({"x": x, "y": y})
# Exclude points where "x" is larger than the slider value.
filtered = source[source["x"] >= slider]

fig = figure()
fig.scatter(x="x", y="y", source=filtered)
show([[fig], [slider]])
```

## License

BokehZen is licensed under the MIT License.

## Alternatives

There are several interactive visualization libraries out there. A few of the big ones are:

- [hvPlot](https://hvplot.holoviz.org/) - BokehZen is heavily inspired by the interactive API of hvPlot and I highly recommend it as an alternative.
- [Bokeh](https://bokeh.org/) - For the purists out there.
- [HoloViews](https://holoviews.org/) - A great data exploration library.
- [Plotly](https://plotly.com/) - An alternative to Bokeh.
