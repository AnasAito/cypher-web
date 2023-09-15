from cypherweb.core.node import Node
from cypherweb.core.graph import Graph


def get_title_candidates(graph):
    return []


class TitleClassifier(Node):
    def __init__(self) -> None:
        pass

    def process(self, graph: Graph) -> None:
        grid_candidates = get_title_candidates(graph)
        # annotate vertices
        attrs = {node: {"type": "title"} for node in grid_candidates}
        graph.set_node_attributes(attrs)
