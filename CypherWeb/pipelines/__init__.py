from cypherweb.core import GraphProcessPipeline, NodeSearchPipeline, Graph

from cypherweb.nodes.html_to_graph import HtmlToGraph
from cypherweb.nodes.connectors import BasicCrawler
from cypherweb.nodes.classifiers import GridClassifier
from cypherweb.nodes.classifiers import LinkListClassifier
from cypherweb.nodes.classifiers import TitleClassifier
from cypherweb.nodes.classifiers import LinkClassifier
from cypherweb.nodes.str_matchers import BaseStrRetriever
from cypherweb.nodes.search import GraphNearestNeighbor
from cypherweb.nodes.cypher import CypherApi

# step 1 : create graph


class CypherWebPipeline:
    def __init__(self):
        graph_pipe = GraphProcessPipeline()

        graph_pipe.add_node(
            BasicCrawler(),
            "crawler",
        )
        graph_pipe.add_node(
            HtmlToGraph(),
            "html_to_graph",
        )
        graph_pipe.add_node(
            GridClassifier(),
            "grid_classifier",
        )
        graph_pipe.add_node(
            LinkListClassifier(),
            "link_list_classifier",
        )
        graph_pipe.add_node(
            TitleClassifier(),
            "title_classifier",
        )
        graph_pipe.add_node(
            LinkClassifier(),
            "link_classifier",
        )

        # # step 2 :  use graph for retrieval
        search_pipe = NodeSearchPipeline()
        search_pipe.add_node(
            CypherApi(),
            "cypher_api",
        )
        search_pipe.add_node(graph_pipe, "graph_process_pipe")
        search_pipe.add_node(
            BaseStrRetriever(),
            "str_matcher",
        )
        search_pipe.add_node(
            GraphNearestNeighbor(),
            "graph_nn",
        )
        self.search_pipe = search_pipe
        self.graph = None

    def run(self, cypher_query: str) -> dict:
        self.search_pipe.run(cypher_query)
        self.graph = self.search_pipe.graph
        return self.search_pipe.passing_input


# results = cypher_search_pipe.run(
#     """
#     USE "https://www.wiz.io/"
#     MATCH (a:Grid)-[e*1..2]->(t:Title)
#     WHERE t.text contains "risks"
#     RETURN a, t
#     """
# )
# print(results)
