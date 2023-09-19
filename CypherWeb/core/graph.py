import networkx as nx


def nx_get_neighbors(graph, node):
    return [{"id": node_id} for node_id in graph.neighbors(node)]


def nx_get_predecessors(graph, node):
    return [{"id": node_id} for node_id in graph.predecessors(node)]


def nx_get_shortest_path(graph, source, target):
    return nx.shortest_path(graph, source, target)


def nx_all_pairs_lowest_common_ancestor(graph, pairs):
    return nx.all_pairs_lowest_common_ancestor(graph, pairs)


def nx_set_node_attributes(graph, attrs):
    nx.set_node_attributes(graph, attrs)


def nx_lowest_common_ancestor(graph, node_ref, node):
    return nx.lowest_common_ancestor(graph, node_ref, node)


BACKEND_MAP = {
    "networkx": {
        "get_neighbors": nx_get_neighbors,
        "get_predecessors": nx_get_predecessors,
        "get_shortest_path": nx_get_shortest_path,
        "all_pairs_lowest_common_ancestor": nx_all_pairs_lowest_common_ancestor,
        "lowest_common_ancestor": nx_lowest_common_ancestor,
        "set_node_attributes": nx_set_node_attributes,
    }
}


class Graph:
    """Graph data structure.
    it is abstracted here so whenever we want to migrate from networkx it is easy

    """

    def __init__(self, page_url: str, backend="networkx") -> None:
        self.page_url = page_url
        self.html_payload = None
        self.backend = backend
        if self.backend == "networkx":
            self._graph = nx.DiGraph()
            # self.nodes = self._graph.nodes
        else:
            raise NotImplementedError

    def get_neighbors(self, node):
        return BACKEND_MAP[self.backend]["get_neighbors"](self._graph, node)

    def get_predecessors(self, node):
        return BACKEND_MAP[self.backend]["get_predecessors"](self._graph, node)

    def get_shortest_path(self, source, target):
        return BACKEND_MAP[self.backend]["get_shortest_path"](
            self._graph, source, target
        )

    def all_pairs_lowest_common_ancestor(self, pairs):
        return BACKEND_MAP[self.backend]["all_pairs_lowest_common_ancestor"](
            self._graph, pairs
        )

    def lowest_common_ancestor(self, node_ref, node):
        return BACKEND_MAP[self.backend]["lowest_common_ancestor"](
            self._graph, node_ref, node
        )

    def set_node_attributes(self, attrs):
        BACKEND_MAP[self.backend]["set_node_attributes"](self._graph, attrs)

    def parent_has_child(self, child_cand, parent):
        return self.lowest_common_ancestor(parent, child_cand) == parent

    def get_nodes_by_type(self, node_type):
        for node in self._graph.nodes:
            try:
                a = node_type in self._graph.nodes[node]["type"]
            except Exception as e:
                print(e)
                print(node)
                print(self._graph.nodes[node])
        return [
            node
            for node in self._graph.nodes
            if node_type in self._graph.nodes[node]["type"]
        ]
