from typing import Dict

from cypherweb.core.node import Node
from cypherweb.core.graph import Graph


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

    def __call__(self, inputs: dict) -> None:
        """Run the pipeline on graph.

        Pipeline will call sequentially enricher on the document.

        doc: instance of Document
            Document to enrich.

        """
        graph = inputs["_start"]["graph"]
        for node in self.dict_nodes.values():
            node(graph)
        return graph


class NodeSearchPipeline:
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
        self.passing_input = None

    def add_node(self, enricher: Node, name: str) -> None:
        """Append ``enricher`` to the pipeline.

        enricher: instance of Node
            Enricher to be called on the document when pipeline is run.

        name: str
            Name ``enricher`` to identify it among the other enrichers.

        """
        self.dict_nodes[name] = {"func": enricher}

    def run(self, page_url: str, params: dict) -> None:
        """Run the pipeline on document"""
        self.graph = Graph(page_url)
        self.passing_input = {"_start": {"page_url": page_url, "graph": self.graph}}
        for node_key, node_val in self.dict_nodes.items():
            _params = params.get(node_key, {})
            node = node_val["func"]
            if isinstance(node, Node):
                output = node(inputs=self.passing_input, params=_params)
                self.passing_input[node_key] = output
            else:
                processed_graph = node(
                    inputs=self.passing_input,
                )
                self.graph = processed_graph
                self.passing_input[node_key] = {"graph": processed_graph}
