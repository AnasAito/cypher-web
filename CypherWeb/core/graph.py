import networkx as nx
from typing import Union


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
        """
        Get the neighbors of a given node.

        Parameters:
            node (any): The node for which to retrieve the neighbors.

        Returns:
            list: A list of the neighbors of the given node.
        """
        return BACKEND_MAP[self.backend]["get_neighbors"](self._graph, node)

    def get_predecessors(self, node):
        """
        Get the predecessors of a given node in the graph.

        Parameters:
            node (Node): The node for which to find the predecessors.

        Returns:
            List[Node]: A list of the predecessors of the given node.
        """
        return BACKEND_MAP[self.backend]["get_predecessors"](self._graph, node)

    def get_shortest_path(self, source, target):
        """
        Get the shortest path between two nodes in the graph.

        :param source: The starting node of the path.
        :type source: Any
        :param target: The target node of the path.
        :type target: Any
        :return: The shortest path between the source and target nodes.
        :rtype: List[Any]
        """
        return BACKEND_MAP[self.backend]["get_shortest_path"](
            self._graph, source, target
        )

    def all_pairs_lowest_common_ancestor(self, pairs):
        """
        Finds the lowest common ancestor for each pair of nodes in the given list.

        :param pairs: A list of pairs, where each pair is a tuple of two nodes.
        :type pairs: list

        :return: A list of lowest common ancestors corresponding to each pair of nodes.
        :rtype: list
        """
        return BACKEND_MAP[self.backend]["all_pairs_lowest_common_ancestor"](
            self._graph, pairs
        )

    def lowest_common_ancestor(self, node_ref, node):
        """
        Find the lowest common ancestor of two nodes in the graph.

        Parameters:
            node_ref (str): The reference node.
            node (str): The node for which to find the lowest common ancestor.

        Returns:
            The lowest common ancestor of the two nodes.
        """
        return BACKEND_MAP[self.backend]["lowest_common_ancestor"](
            self._graph, node_ref, node
        )

    def set_node_attributes(self, attrs):
        """
        Set attributes on all nodes in the graph.

        Parameters:
            attrs (dict): A dictionary of attribute-value pairs to set for each node.

        Returns:
            None
        """
        BACKEND_MAP[self.backend]["set_node_attributes"](self._graph, attrs)

    def parent_has_child(self, child_cand, parent):
        """
        Check if a parent node has a specific child node.

        Args:
            child_cand: The child node to check for.
            parent: The parent node to check against.

        Returns:
            True if the parent node has the child node, False otherwise.
        """
        return self.lowest_common_ancestor(parent, child_cand) == parent

    def get_nodes_by_type(self, node_type: Union[str, list]):
        """
        Get nodes from the graph that match the specified node type(s).

        Args:
            node_type (Union[str, list]): The type(s) of nodes to retrieve.

        Returns:
            list: A list of dictionaries representing the matching nodes. Each dictionary
            contains the "id" and "type" of a node.
        """
        if type(node_type) == str:
            node_type = [node_type]

        def intersection(lst1, lst2):
            return list(set(lst1) & set(lst2))

        return [
            {
                "id": node,
                "type": intersection(node_type, self._graph.nodes[node]["type"])[0],
            }
            for node in self._graph.nodes
            if len(intersection(node_type, self._graph.nodes[node]["type"])) > 0
        ]
