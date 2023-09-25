
<section align="center">

# ``CypherWeb``

## A Cypher layer to query the web

[**Live demo**](https://cypher-web.streamlit.app/)

</section>

### Important Note:
This repository is currently a work in progress.
While you can use it for some basic yet good enough queries, I'm still sketching a proper dev roadmap for it that I can share with interested members of the community.

The reason for this premature release is that to share the main idea behind the project with the community.
Upcoming development will enhance it and make this tool usable in production environments.

A detailed article is soon to be published on how cypherweb works...

### The key problem:
The key problem that cypherweb is trying to solve is very simple: we take for granted HTML data, in other words, we treat it as unstructured text and don't make use of its semistructured format.


![build](https://github.com/AnasAito/skillner/workflows/tests/badge.svg)
[![Downloads](https://static.pepy.tech/badge/cypherweb)](https://pepy.tech/project/cypherweb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)



## Install

Run the following command to get the latest version ``cypherweb``
```bash
pip install cypherweb -U
```
## Example of usage

If you are familiar with Cypher language, using cypherWeb will be easy.

Let’s say you are interested in extracting some team members' data from a set of websites.
Instead of building custom templates specific to each website, cypherweb will ease this.
We know that usually team members are presented as grids, which could be a set of ``li`` elements or custom HTML elements that share the same style or inner structure.

Let's test the extraction using an example.

```python
# test new restruction
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
from rich import print as rprint

# step 1: create graph
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

# step 2:  use graph for retrieval
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


# use your pipeline
search_pipe.run(
"""
USE "https://weaviate.io/company/about-us"
MATCH (a:Grid)-[e*1..2]->(t:Title)
WHERE t.text contains "team"
RETURN a, t
"""
)
rprint(search_pipe.passing_input)

# preview your select HTML element as string
# visualize node
from cypherweb.utils.visualizations import render_element_from_root

node_id = "div_66321657"
graph = search_pipe.graph._graph
str_agg = ""
render_element_from_root(graph, node_id, str_agg=str_agg, depth=0)
```

## Supported queries:

As a start, cypherweb supports two types of queries
- Search for a typed/non-typed element using a filter on its text content.
```cypher
USE "https://weaviate.io/company/about-us"
MATCH (a:Grid)
WHERE a.text contains "feature a"
RETURN a
```
- Search for a typed/non-typed element using its links to other elements.
```cypher
USE "https://weaviate.io/company/about-us"
MATCH (a:Grid)-[e*1..2]->(t:Title)
WHERE t.text contains "team"
RETURN a, t
```

The currently supported elements are
- Grids ``Grid``
- Titles (headings for now) ``Title``
- Links ``Link``
- list of links ``ListLink``

## Work in progress

- Add more consumer nodes (HTML consumer, Structured consumer (Python dict,JSON...))
- Add/improve classifier nodes (paragraph detection,titles)
- improve Cypher node (instead of a hardcoded transformation we can use native graph traversal supported by networkx (graph motifs))
