from cypherweb.core.node import Node


class GraphNearestNeighbor(Node):
    def __init__(self) -> None:
        pass

    def get_distance(self, graph, node_down, node_up):
        distance = 0
        while node_down != node_up:
            node_down = graph.get_predecessors(node_down)[0]["id"]
            # print(node_down)
            distance += 1
        return distance

    def score_pairs_of_nodes(self, graph, node_ref, node):
        # Note : nodes within grid will return 0
        ancestor = graph.lowest_common_ancestor(node_ref, node)
        # compute distance
        # print(ancestor)
        return self.get_distance(graph, node, ancestor)

    def run(self, payload: dict, params: dict = None) -> dict:
        if "str_matcher" in payload:
            output = {}
            top_k_anchors = params["top_k_anchors"]
            node_type = params["node_type"]
            anchor_nodes = payload["str_matcher"]["anchor_nodes"][:top_k_anchors]
            graph = payload["graph_process_pipe"]["graph"]
            cand_nodes = [node for node in graph.get_nodes_by_type(node_type)]

            for anchor_node in anchor_nodes:
                anchor_node, score, snippet = anchor_node
                results = {}
                for grid_node in cand_nodes:
                    # print(grid_node)
                    distance = self.score_pairs_of_nodes(graph, anchor_node, grid_node)
                    # print(distance)
                    if (
                        distance != 0
                    ):  # TODO we should solve why main node is a grid ? then we can activate again
                        results[grid_node] = distance
                    # print("-------------------")
                # sort by distance
                results = sorted(results.items(), key=lambda item: item[1])
                # get min dist
                min_dist = results[0][1]
                best_grids = [
                    {"node": node, "distance": distance}
                    for node, distance in results
                    if distance == min_dist
                ]
                output[anchor_node] = best_grids
            return {f"{node_type}_results": output}
