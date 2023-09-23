from cypherweb.core.node import Node
from cypherweb.core.graph import Graph
import re


def is_elem_heading(string):
    """
    Check if the given string is a heading element.

    Parameters:
        string (str): The string to be checked.

    Returns:
        bool: True if the string is a heading element, False otherwise.
    """
    string = string.lower()
    # Define a regular expression pattern to match h1 to h6 headings
    heading_pattern = r"^h[1-6]$"

    # Use re.match to check if the entire string matches the pattern
    return bool(re.match(heading_pattern, string))


def get_title_candidates(graph):
    """
    Returns a list of title candidates from the given graph.

    Args:
        graph (Graph): The graph object containing the nodes.

    Returns:
        list: A list of nodes that are considered title candidates.
    """
    # TODO : add more heuritics to detect titles (token count + 0 links within element as proxy ?)
    return [
        node
        for node in graph._graph.nodes
        if is_elem_heading(graph._graph.nodes[node].get("element_type"))
    ]


class TitleClassifier(Node):
    def __init__(self) -> None:
        pass

    def process(self, graph: Graph) -> None:
        """
        Process the given graph by annotating the vertices with title attributes.

        Args:
            graph (Graph): The graph to be processed.

        Returns:
            None
        """
        title_candidates = get_title_candidates(graph)
        # annotate vertices
        # attrs = {
        #     node: {"type": ["title"] + graph._graph.nodes[node]["type"]}
        #     for node in title_candidates
        # }
        attrs = {}
        for node in title_candidates:
            attrs[node] = {"type": ["title"] + graph._graph.nodes[node]["type"]}
            if not graph._graph.nodes[node].get("payload"):
                # handle title wrapper
                # get all childs
                title_childs = [child["id"] for child in graph.get_neighbors(node)]
                node_text = [
                    graph._graph.nodes[child]["payload"]["text"]
                    for child in title_childs
                ]
                attrs[node]["payload"] = {
                    "text": " ".join(node_text),
                    "href": None,
                    "alt": None,
                }

        graph.set_node_attributes(attrs)
