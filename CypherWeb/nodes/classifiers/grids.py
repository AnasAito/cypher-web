from collections import Counter
import itertools
from cypherweb.core.node import Node
from cypherweb.core.graph import Graph


def get_pseudo_class(graph, node):
    try:
        return graph._graph.nodes[node]["class"][0]
    except Exception as e:
        # print("get_pseudo_class", e)
        return None


def get_grid_candidates(raw_graph):
    # step 1 : get leaf nodes
    nodes_with_payload = [
        node
        for node in raw_graph._graph.nodes
        if raw_graph._graph.nodes[node].get("payload") is not None
    ]
    # step 2 : get dist from root and cluster nodes based on dist_to_root
    clusters = {}
    root_node = [
        node
        for node in raw_graph._graph.nodes
        if raw_graph._graph.nodes[node].get("is_root")
    ][0]
    for node in nodes_with_payload:
        path = raw_graph.get_shortest_path(source=root_node, target=node)
        # print(path)
        dist_to_root = len(path)
        if f"dist_{dist_to_root}" not in clusters:
            clusters[f"dist_{dist_to_root}"] = [node]
        else:
            clusters[f"dist_{dist_to_root}"].append(node)

    # # step3 : get common ancestor for each cluster
    incestors_scores = Counter()
    for nodes in clusters.values():
        # get all pairs
        pairs = list(itertools.combinations(nodes, 2))
        incestors = dict(raw_graph.all_pairs_lowest_common_ancestor(pairs))
        for inc in incestors.values():
            incestors_scores[inc] += 1
    # rprint(incestors_scores)
    # step 4 : filter candidates with 0 entropy (same child type)
    grid_cands = {}
    for inc in incestors_scores:
        inc_neighbors = raw_graph.get_neighbors(inc)
        zero_entropy = (
            len(set([node["id"].split("_")[0] for node in inc_neighbors])) == 1
            and len(
                set([get_pseudo_class(raw_graph, node["id"]) for node in inc_neighbors])
            )
            == 1
        )

        if zero_entropy:
            grid_cands[inc] = len(inc_neighbors)
    return grid_cands


from rich import print as rprint


class GridClassifier(Node):
    def __init__(self) -> None:
        pass

    def process(self, graph: Graph) -> None:
        grid_candidates = get_grid_candidates(graph)
        # annotate vertices
        attrs = {
            node: {"type": ["grid"] + graph._graph.nodes[node]["type"]}
            for node in grid_candidates
        }

        graph.set_node_attributes(attrs)
