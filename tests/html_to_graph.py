import unittest
from bs4 import BeautifulSoup
from collections import defaultdict
import networkx as nx
from CypherWeb.html_to_graph import traverse_html


class TestHtmlToGraph(unittest.TestCase):
    def test_html_to_graph(self):
        graph_nodes_expected = [
            "a_None_[]",
            "body_None_[]",
            "p_None_[]",
            "span_None_[]",
            "p_1_[]",
            "div_None_[]",
            "p_2_[]",
            "p_3_['classy']",
        ]
        graph_edges_expected = [
            ("a_None_[]", "p_None_[]"),
            ("a_None_[]", "span_None_[]"),
            ("body_None_[]", "a_None_[]"),
            ("body_None_[]", "div_None_[]"),
            ("span_None_[]", "p_1_[]"),
            ("div_None_[]", "p_2_[]"),
            ("div_None_[]", "p_3_['classy']"),
        ]
        page = """
        <body>
        <a href="newcomments" id="tag-12">comments <span>tsty_sân</span></a>
        <div>
        raw text
        <p class="classy">text wrapped</p>
        <img src ='test.img'/>
        </div>
        </body>
        """

        soup = BeautifulSoup(page, "html.parser")
        raw_graph = nx.DiGraph()
        _global_counter = 0
        traverse_html(soup, raw_graph, defaultdict(int), _global_counter)

        # Assertions on raw_graph.nodes and raw_graph.edges
        self.assertListEqual(sorted(raw_graph.nodes), sorted(graph_nodes_expected))
        self.assertListEqual(sorted(raw_graph.edges), sorted(graph_edges_expected))


if __name__ == "__main__":
    unittest.main()
