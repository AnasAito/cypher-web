from cypherweb.core.node import Node
from cypherweb.core.graph import Graph


def get_link_list_candidates(graph):
    return []


class LinkListClassifier(Node):
    def __init__(self) -> None:
        pass

    def process(self, graph: Graph) -> None:
        grid_candidates = get_link_list_candidates(graph)
        # annotate vertices
        attrs = {node: {"type": "link_list"} for node in grid_candidates}
        graph.set_node_attributes(attrs)
