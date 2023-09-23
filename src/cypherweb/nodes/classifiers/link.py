from cypherweb.core.node import Node
from cypherweb.core.graph import Graph


def node_is_link(graph, node_id):
    return graph._graph.nodes[node_id]["element_type"] == "a"


def get_link_list_candidates(graph):
    """
    Generate a list of candidates for link nodes in the given graph.

    Parameters:
        graph (Graph): The graph from which to generate the candidates.

    Returns:
        list: A list of nodes that are candidates for link nodes.
    """
    return [node for node in graph._graph.nodes if node_is_link(graph, node)]


class LinkClassifier(Node):
    def __init__(self) -> None:
        pass

    def process(self, graph: Graph) -> None:
        """
        Process the given graph by annotating the vertices with specific attributes.

        Parameters:
            graph (Graph): The graph to be processed.

        Returns:
            None
        """
        grid_candidates = get_link_list_candidates(graph)
        # annotate vertices
        attrs = {
            node: {"type": ["link"] + graph._graph.nodes[node]["type"]}
            for node in grid_candidates
        }

        graph.set_node_attributes(attrs)
