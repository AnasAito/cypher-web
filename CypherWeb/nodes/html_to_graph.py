from cypherweb.core.node import Node
from cypherweb.core.graph import Graph

from cypherweb.utils.html_to_graph import traverse_html, clean_graph
from rich import print as rprint
from bs4 import BeautifulSoup
from collections import defaultdict


class HtmlToGraph(Node):
    def __init__(self) -> None:
        pass

    def process(self, graph: Graph) -> None:
        html_payload = graph.html_payload
        soup = BeautifulSoup(html_payload, "html.parser")  # .body
        # rprint(soup)
        _global_counter = 0
        traverse_html(
            soup, graph._graph, defaultdict(int), _global_counter, hash_ids=True
        )
        graph._graph = clean_graph(graph._graph)

        # attrs = {node: {"type": []} for node in graph._graph.nodes}
        # graph.set_node_attributes(attrs)
