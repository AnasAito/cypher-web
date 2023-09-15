from cypherweb.core.node import Node
from cypherweb.core.graph import Graph
import re


def is_elem_heading(string):
    string = string.lower()
    # Define a regular expression pattern to match h1 to h6 headings
    heading_pattern = r"^h[1-6]$"

    # Use re.match to check if the entire string matches the pattern
    return bool(re.match(heading_pattern, string))


def get_title_candidates(graph):
    return [
        node
        for node in graph._graph.nodes
        if is_elem_heading(graph._graph.nodes[node].get("element_type"))
    ]


class TitleClassifier(Node):
    def __init__(self) -> None:
        pass

    def process(self, graph: Graph) -> None:
        grid_candidates = get_title_candidates(graph)
        # annotate vertices
        attrs = {
            node: {"type": ["title"] + graph._graph.nodes[node]["type"]}
            for node in grid_candidates
        }
        graph.set_node_attributes(attrs)
