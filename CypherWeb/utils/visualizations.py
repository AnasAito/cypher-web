from .html_to_graph import get_neighbors


def render_element_from_root(graph, element, depth=0):
    indent = "    " * depth
    element_name = graph.nodes[element]["element_type"]
    indent = "    " * depth
    rectangle = "*" * (len(indent) + len(element_name) + 2)
    print(rectangle)
    try:
        payload = graph.nodes[element]["payload"]["text"]
        if element_name == "a":
            payload = graph.nodes[element]["payload"]["href"]
        if element_name == "img":
            payload = graph.nodes[element]["payload"]["alt"]
    except:
        payload = None
    print(indent + f"* {element_name} / {payload} *")
    print(rectangle)
    for child in get_neighbors(graph, element):
        child = child["id"]
        keep_traversing = graph.nodes[child]["element_type"]
        if keep_traversing:
            render_element_from_root(graph, child, depth + 1)
