import operator

from bokeh.models import CustomJS, Dropdown

from ._comparison import isin

_operator_map = {
    operator.lt: "<",
    operator.le: "<=",
    operator.eq: "===",
    operator.ne: "!==",
    operator.ge: ">=",
    operator.gt: ">",
}

_CHECKBOX_CONTAINS = """
export default ({widget, source, column, index_filter}, obj, data, context) => {
    const labels = []
    for (const i of widget["active"]) {
        labels.push(widget["labels"][i])
    }

    const indices = []
    for (const [i, value] of source.data[column].entries()) {
        if (labels.includes(value)) {
            indices.push(i)
        }
    }
    index_filter.indices = indices
}
"""


def checkbox_filter(widget, source, column, index_filter):
    callback_args = dict(
        widget=widget, source=source, column=column, index_filter=index_filter
    )
    callback = CustomJS(args=callback_args, code=_CHECKBOX_CONTAINS)
    widget.js_on_change("active", callback)

    return index_filter


_DROPDOWN_CONTAINS = """
export default ({widget, source, column, index_filter}, obj, data, context) => {
    const item = obj["item"]
    const indices = []
    for (const [i, value] of source.data[column].entries()) {
        if (item.includes(value)) {
            indices.push(i)
        }
    }
    index_filter.indices = indices
}
"""

_DROPDOWN_COMPARISON = """
export default ({{widget, source, column, index_filter}}, obj, data, context) => {{
    const item = obj["item"]
    const indices = []
    for (const [i, value] of source.data[column].entries()) {{
        if (value {comparison} item) {{
            indices.push(i)
        }}
    }}
    index_filter.indices = indices
}}
"""


def dropdown_filter(widget, source, column, index_filter, op):
    if op is isin:
        code = _DROPDOWN_CONTAINS
    else:
        code = _DROPDOWN_COMPARISON.format(comparison=_operator_map[op])

    callback_args = dict(
        widget=widget, source=source, column=column, index_filter=index_filter
    )
    callback = CustomJS(args=callback_args, code=code)
    widget.js_on_event("menu_item_click", callback)

    return index_filter


def multichoice_filter(widget, source, column, index_filter):
    callback_args = dict(
        widget=widget, source=source, column=column, index_filter=index_filter
    )
    callback = CustomJS(args=callback_args, code=_MULTICHOICE_CONTAINS)
    widget.js_on_change("value", callback)

    return index_filter
