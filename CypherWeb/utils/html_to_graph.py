import networkx as nx
import re
from collections import defaultdict
import itertools
import hashlib


NOT_PERMITED_TAGS = [
    "script",
    # "img",
    "noscript",
    "svg",
    "input",
    "style",
    "kin-address-form",
    "picture",
    # "button",
]
NOT_PERMITED_TEXTS = [
    "view",
    "x",
    "apply",
    "view",
    "apply",
    "sort by",
    "skip",
    "skip to content",
    "skip to navigation menu",
    "×",
    "cancel",
    "sort/view",
    "filter",
]


def hash_element(element_id):
    return int(hashlib.sha1(element_id.encode("utf-8")).hexdigest(), 16) % (10**8)
    # return hashlib.sha1(element_id.encode("utf-8")).hexdigest()


def has_payload(element, except_nodes=["a"]):
    """
    only capture payload if element is leaf
    """
    if isinstance(
        element, str
    ):  # hot fix for ('NavigableString' object has no attribute 'contents')
        return True

    return len(element.findChildren()) == 0 or element.name in except_nodes


def format_text(text):
    text = text.replace("\n", " ").strip()
    return " ".join(re.split("\s+", text, flags=re.UNICODE)).strip()


def get_payload(node):
    if isinstance(node, str):
        return {"href": None, "text": format_text(node.text), "alt": None, "src": None}
    return {
        "href": node.get("href"),
        "text": format_text(node.text),
        "alt": node.get("alt"),
        "src": node.get("src"),
    }


def normalize_element(soup_element):
    def is_valid_text_element(soup_element):
        return soup_element.text == soup_element and soup_element.text.strip() != ""

    def is_valid_tag(soup_element):
        if soup_element.name is None:
            return is_valid_text_element(soup_element)
        return soup_element.name not in NOT_PERMITED_TAGS

    def is_valid_text(soup_element):
        return soup_element.text.strip().lower() not in NOT_PERMITED_TEXTS

    is_valid = is_valid_tag(soup_element) and is_valid_text(soup_element)

    return {
        "is_valid": is_valid,
        "content": soup_element if is_valid else soup_element.text,
        "is_raw_text": is_valid_text_element(soup_element),
    }


def traverse_html(
    _soup, _graph: nx.Graph, _counter, global_counter, _parent=None, hash_ids=False
) -> None:
    """
    Traverses an HTML element using depth-first search and populates a graph with the element information.

    Args:
        _soup (BeautifulSoup): The BeautifulSoup object representing the HTML.
        _graph (nx.Graph): The graph to populate with the element information.
        _counter (Dict[str, int]): A dictionary to keep track of the count of each element type encountered.
        global_counter (int): The global counter to assign unique item indices to each element.
        _parent (Optional[str]): The parent node ID in the graph. Defaults to None.
        hash_ids (bool): Indicates whether to hash the node IDs. Defaults to False.

    Returns:
        None: This function does not return any value.
    """
    for element in _soup.contents:
        element_norm = normalize_element(element)

        if element_norm["is_valid"]:
            element_content = element_norm["content"]
            if element_norm["is_raw_text"]:
                element_name = "p"
                element_class = []
            else:
                element_name = element_content.name
                element_class = element_content.get("class", [])

            _name_count = _counter.get(element_name)
            _element_name = f"{element_name}_{_name_count}_{element_class}"
            node_id = _element_name
            if hash_ids:
                node_id = f"{element_name}_{hash_element(_element_name)}"  # hash name

            ## entry_point
            if (
                _parent is None
            ):  # and len(_graph.nodes) == 0: # disable this since some nodes may be orphan
                # print(node_id)
                payload = (
                    get_payload(element_content)
                    if has_payload(element_content)
                    else None
                )
                _graph.add_nodes_from(
                    [
                        (
                            node_id,
                            {
                                "element_type": element_name,
                                "element_name": _element_name,
                                "item_index": global_counter,
                                "class": "_CLASSJOIN_".join(element_class),
                                "payload": payload,
                                "is_root": True,
                                "type": [],
                            },
                        )
                    ]
                )
                global_counter += 1

            if _parent is not None:
                payload = (
                    get_payload(element_content)
                    if has_payload(element_content)
                    else None
                )
                _graph.add_nodes_from(
                    [
                        (
                            node_id,
                            {
                                "element_type": element_name,
                                "element_name": _element_name,
                                "item_index": global_counter,
                                "class": element_class,
                                "payload": payload,
                                "is_root": False,
                                "type": [],
                            },
                        )
                    ]
                )

                global_counter += 1
                _graph.add_edge(_parent, node_id)

            _counter[element_name] += 1
            if not element_norm["is_raw_text"] and len(element.findChildren()) != 0:
                traverse_html(
                    element_content,
                    _graph,
                    _counter,
                    global_counter,
                    node_id,
                    hash_ids=hash_ids,
                )


def get_neighbors(graph, node):
    """
    Given a graph and a node, this function returns a list of dictionaries representing the neighbors of the given node.

    :param graph: A networkx graph object representing the graph.
    :type graph: networkx.Graph
    :param node: The node whose neighbors we want to retrieve.
    :type node: Any hashable object that is a node in the graph.
    :return: A list of dictionaries representing the neighbors of the given node. Each dictionary contains the keys 'id' and 'meta' which correspond to the id of the neighbor and its metadata respectively.
    :rtype: List[Dict[str, Union[Hashable, Any]]]
    """
    return [{"id": node_id} for node_id in graph.neighbors(node)]


def get_predecessors(graph, node):
    """
    Returns a list of dictionaries representing the predecessors of a given node in a directed graph.

    :param graph: A directed graph object.
    :type graph: networkx.DiGraph
    :param node: A node in the graph whose predecessors are to be found.
    :type node: Any hashable object
    :return: A list of dictionaries where each dictionary contains the id and meta data of a predecessor node.
    :rtype: List[Dict[str,Any]]
    """
    return [{"id": node_id} for node_id in graph.predecessors(node)]


def clean_graph(graph, only_intermediate=False, node_type_exceptions=["a"]):
    """
    Deletes nodes from a graph that satisfy certain conditions. Nodes that are empty leaves or bridge nodes are removed.
    If `only_intermediate` is True, only bridge nodes are deleted.

    Args:
    - graph: a networkx graph object.
    - only_intermediate: a boolean indicating whether or not to only delete intermediate nodes (default: False).

    Returns:
    - graph: the modified networkx graph with the nodes deleted.
    """

    def is_empty_leaf(node):
        return (
            graph.nodes[node].get("payload") is None
            and len(get_neighbors(graph, node)) == 0
        )

    # def is_bridge_node(node):
    #     return graph.nodes[node]["payload"] is None and len(
    #         get_predecessors(graph, node)
    #     ) == len(get_neighbors(graph, node))
    def is_bridge_node(node):
        return len(get_predecessors(graph, node)) == len(get_neighbors(graph, node))

    if only_intermediate:
        nodes_to_delete = [node for node in graph.nodes if is_bridge_node(node)]
    else:
        nodes_to_delete = [
            node for node in graph.nodes if is_empty_leaf(node) or is_bridge_node(node)
        ]
    # print(nodes_to_delete)
    node_type_exceptions
    nodes_to_delete = [
        node
        for node in nodes_to_delete
        if graph.nodes[node]["element_type"] not in node_type_exceptions
    ]
    for node in nodes_to_delete:
        # print(node)
        try:
            graph.add_edges_from(
                itertools.product(graph.predecessors(node), graph.successors(node))
            )
            # update successors class
            for successor in graph.successors(node):
                graph.nodes[successor]["class"] = (
                    graph.nodes[node]["class"] + graph.nodes[successor]["class"]
                )
                # inherit root_status
                graph.nodes[successor]["is_root"] = (
                    graph.nodes[node]["is_root"] or graph.nodes[successor]["is_root"]
                )
            graph.remove_node(node)
        except KeyError as e:
            print(e)
            pass

    # post root re-election
    for node in graph.nodes:
        if len(get_predecessors(graph, node)) == 0:
            # print(node, graph.nodes[node])
            graph.nodes[node]["is_root"] = True

    return graph
