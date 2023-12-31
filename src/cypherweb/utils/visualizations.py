from .html_to_graph import get_neighbors


def render_element_from_root(graph, element, str_agg, depth=0):
    """
    Render an element and its children as string.

    Args:
        graph (networkx.Graph): The graph containing the elements.
        element (str): The ID of the element to render.

    Returns:
        None

    Raises:
        None

    """
    indent = "    " * depth
    element_name = graph.nodes[element]["element_type"]
    indent = "    " * depth
    rectangle = "*" * (len(indent) + len(element_name) + 2)
    print(rectangle)
    str_agg += "\n" + rectangle
    try:
        payload = graph.nodes[element]["payload"]["text"]
        if element_name == "a":
            payload = graph.nodes[element]["payload"]["href"]
        if element_name == "img":
            payload = graph.nodes[element]["payload"]["alt"]
    except:
        payload = ""
    print(indent + f"* {element_name} / {payload} *")
    print(rectangle)
    str_agg += "\n" + indent + f"{element_name} / {payload}"
    str_agg += "\n" + rectangle
    for child in get_neighbors(graph, element):
        child = child["id"]
        keep_traversing = graph.nodes[child]["element_type"]
        if keep_traversing:
            str_agg = render_element_from_root(
                graph=graph, element=child, depth=depth + 1, str_agg=str_agg
            )
    return str_agg
