from typing import Dict, Union

from cypherweb.core.node import Node
from cypherweb.core.graph import Graph
from cypherweb.core.url import Url
import time


class GraphProcessPipeline:
    """Pipeline class to define the way of enriching documents.

    The pipeline defines sequential way of enriching documents.

    Attributes
    ----------
    dict_nodes: Dict[str, Node]
        A dictionary that stores the enrichers (nodes) and their
        corresponding names.

    """

    def __init__(self) -> None:
        self.dict_nodes: Dict[str, Node] = {}
        self.graph = None

    def add_node(self, enricher: Node, name: str) -> None:
        """Append ``enricher`` to the pipeline.

        enricher: instance of Node
            Enricher to be called on the document when pipeline is run.

        name: str
            Name ``enricher`` to identify it among the other enrichers.

        """
        self.dict_nodes[name] = enricher

    def process(self, graph: Graph) -> None:
        """Run the pipeline on graph. [if used as stand-alone]

        Pipeline will call sequentially enricher on the document.

        doc: instance of Document
            Document to enrich.

        """
        for node in self.dict_nodes.values():
            node(graph)

    def build(self, url: Url) -> None:
        """Run the pipeline on graph.

        Pipeline will call sequentially enricher on the document.

        doc: instance of Document
            Document to enrich.

        """
        graph = Graph(url.page_url)
        for node in self.dict_nodes.values():
            node(graph)
        return graph


class NodeSearchPipeline:
    """pipeline defines sequential way of enriching/consuming the graph.


    Attributes
    ----------
    dict_nodes: Dict[str, Node]
        A dictionary that stores the enrichers (nodes) and their
        corresponding names.

    """

    def __init__(self) -> None:
        self.dict_nodes: Dict[str, Node] = {}
        self.passing_input = None

    def add_node(self, enricher: Node, name: str) -> None:
        """Append ``enricher`` to the pipeline.

        enricher: instance of Node
            Enricher to be called on the graph when pipeline is run.

        name: str
            Name ``enricher`` to identify it among the other enrichers.

        """
        self.dict_nodes[name] = {"func": enricher}

    def run(self, graph, query: Union[dict, str]) -> None:
        """Run the pipeline on document"""

        if type(query) == str and "cypher_api" in self.dict_nodes:
            output = self.dict_nodes["cypher_api"]["func"](
                inputs=query, params={})
            # prepare page_url , params
            # page_url = output["page_url"]
            params = output["params"]
            # remove "cypher_api"
            self.dict_nodes = {
                k: v for k, v in self.dict_nodes.items() if k != "cypher_api"
            }

            pass
        if type(query) == dict:
            # page_url = query["page_url"]
            params = query["params"]

        self.graph = graph
        self.passing_input = {"graph_process_pipe": {
            "page_url": None, "graph": self.graph}}
        for node_key, node_val in self.dict_nodes.items():
            # compute time for each node
            start_time = time.time()
            _params = params.get(node_key, {})
            node = node_val["func"]
            output = node(inputs=self.passing_input, params=_params)
            end_time = time.time()
            delta_time = end_time - start_time
            delta_time = str(round(delta_time * 1000, 2)) + "ms"
            output["run_time"] = delta_time
            self.passing_input[node_key] = output
        return self.passing_input
