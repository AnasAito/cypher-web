from cypherweb.core.node import Node


class GraphNearestNeighbor(Node):
    def __init__(self) -> None:
        pass

    def get_distance(self, graph, node_down, node_up):
        """
        Calculates the distance between two nodes in a graph.

        Parameters:
            graph (Graph): The graph object representing the graph.
            node_down (int): The starting node.
            node_up (int): The target node.

        Returns:
            int: The distance between the two nodes.
        """
        distance = 0
        while node_down != node_up:
            node_down = graph.get_predecessors(node_down)[0]["id"]
            distance += 1
        return distance

    def score_pairs_of_nodes(self, graph, node_ref, node):
        """
        Calculates the score for pairs of nodes in a graph.

        Parameters:
            graph (Graph): The graph object representing the graph.
            node_ref (Node): The reference node.
            node (Node): The node to compare with the reference node.

        Returns:
            dict: A dictionary containing the following keys:
                - dist (int): The maximum distance between the node and the reference node.
                - anchor_dist (int): The distance between the reference node and the lowest common ancestor of the node and the reference node.
        """
        ancestor = graph.lowest_common_ancestor(node_ref, node)
        if ancestor == node:  # Note : nodes within element will return 0
            return {
                "dist": self.get_distance(graph, node_ref, ancestor),
                "anchor_dist": self.get_distance(graph, node_ref, ancestor),
            }
        ances_node_dist = self.get_distance(graph, node, ancestor)
        ances_ref_dist = self.get_distance(graph, node_ref, ancestor)
        return {
            "dist": max(ances_node_dist, ances_ref_dist),
            "anchor_dist": ances_ref_dist,
        }

    def run(self, payload: dict, params: dict = None) -> dict:
        """
        Runs the function with the given payload and parameters.

        Args:
            payload (dict): The payload for the function.
            params (dict, optional): The parameters for the function. Defaults to None.

        Returns:
            dict: list of matched nodes

        """
        if "str_matcher" in payload:
            output = {}
            top_k_anchors = params["top_k_anchors"]
            node_type = params["node_type"]
            node_include = params["node_include"]
            anchor_nodes = payload["str_matcher"]["anchor_nodes"][:top_k_anchors]
            graph = payload["graph_process_pipe"]["graph"]
            cand_nodes = [node for node in graph.get_nodes_by_type(node_type)]
            # TODO : if type is node defined use all elements
            if len(cand_nodes) == 0:
                return {f"{node_type}_results": []}
            for anchor_node in anchor_nodes:
                anchor_node, score, snippet = anchor_node
                results = {}
                for cand_node in cand_nodes:
                    cand_node_id = cand_node["id"]
                    # print(grid_node)
                    distance_meta = self.score_pairs_of_nodes(
                        graph, anchor_node, cand_node_id
                    )
                    # add child count to distance
                    distance_meta["childs_count"] = len(
                        graph.get_neighbors(cand_node_id)
                    )
                    # add type to distance as meta
                    distance_meta["type"] = cand_node["type"]
                    results[cand_node_id] = distance_meta
                    # print("-------------------")

                # sort by distance
                results = sorted(
                    results.items(),
                    key=lambda item: (
                        item[1]["anchor_dist"],
                        item[1]["dist"],
                        -item[1]["childs_count"],
                    ),
                )
                # get min dist
                min_dist = results[0][1]  # ["dist"]

                best_nodes = [
                    {
                        "node": node,
                        "distance": distance,
                    }
                    for node, distance in results
                    if distance["dist"] == min_dist["dist"]
                    and (
                        not node_include
                        or graph.parent_has_child(child_cand=anchor_node, parent=node)
                    )
                    and distance["anchor_dist"] == min_dist["anchor_dist"]
                ]
                # TODO: remove sub childs duplciat
                output[anchor_node] = best_nodes
            return {f"{node_type}_results": output}
