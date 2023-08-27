from collections import defaultdict, Counter
import networkx as nx
import itertools
from .html_to_graph import get_neighbors


def get_pseudo_class(graph, node):
    try:
        return graph.nodes[node]["class"][0]
    except:
        return None


def get_grid_candidates(raw_graph):
    # step 1 : get leaf nodes
    nodes_with_payload = [
        node for node in raw_graph.nodes if raw_graph.nodes[node]["payload"] is not None
    ]
    # step 2 : get dist from root and cluster nodes based on dist_to_root
    clusters = {}
    root_node = [node for node in raw_graph.nodes if raw_graph.nodes[node]["is_root"]][
        0
    ]
    for node in nodes_with_payload:
        path = nx.shortest_path(raw_graph, source=root_node, target=node)
        # print(path)
        dist_to_root = len(path)
        if f"dist_{dist_to_root}" not in clusters:
            clusters[f"dist_{dist_to_root}"] = [node]
        else:
            clusters[f"dist_{dist_to_root}"].append(node)

    # rprint(clusters)

    # # step3 : get common ancestor for each cluster
    incestors_scores = Counter()
    for nodes in clusters.values():
        # get all pairs
        pairs = list(itertools.combinations(nodes, 2))
        incestors = dict(nx.all_pairs_lowest_common_ancestor(raw_graph, pairs))
        for inc in incestors.values():
            incestors_scores[inc] += 1
    # rprint(incestors_scores)
    # step 4 : filter candidates with 0 entropy (same child type)
    grid_cands = {}
    for inc in incestors_scores:
        zero_entropy = (
            len(
                set(
                    [node["id"].split("_")[0] for node in get_neighbors(raw_graph, inc)]
                )
            )
            == 1
            and len(
                set(
                    [
                        get_pseudo_class(raw_graph, node["id"])
                        for node in get_neighbors(raw_graph, inc)
                    ]
                )
            )
            == 1
        )

        if zero_entropy:
            # rprint(inc,[raw_graph.nodes[node['id']] for node in get_neighbors(raw_graph, inc)])
            grid_cands[inc] = incestors_scores[inc]
    return grid_cands
