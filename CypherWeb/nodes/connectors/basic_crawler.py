from cypherweb.core.node import Node
from cypherweb.core.graph import Graph
import requests


def get_page(page_url):
    """
    Retrieve the text content of a webpage.
    """
    headers = {
        "User-Agent": "Mozilla/5.0",
    }
    try:
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


class BasicCrawler(Node):
    def __init__(self) -> None:
        pass

    def process(self, graph: Graph) -> None:
        """
        Process the given graph by retrieving the HTML payload of the page URL.

        Args:
            graph (Graph): The graph object representing the web page.

        Returns:
            None
        """
        page_url = graph.page_url
        html_payload = get_page(page_url)
        graph.html_payload = html_payload
