from cypherweb.core.node import Node


class BaseStrRetriever(Node):
    def __init__(self) -> None:
        pass

    def score_text_against_query(
        self,
        text,
        query,
        str_match_type,
        str_lower=False,
    ):
        if str_lower:
            text = text.lower()
            query = query.lower()
        if str_match_type == "exact" and query in text:
            win_size = 50
            start = max(text.index(query) - win_size, 0)
            end = min(text.index(query) + win_size + len(query), len(text))
            return (
                1 * (query == text),
                f"...{text[start:end]}...",
            )
        elif str_match_type == "contains" and query in text:
            win_size = 50
            start = max(text.index(query) - win_size, 0)
            end = min(text.index(query) + win_size + len(query), len(text))
            return (
                1 * (query in text) * (len(query) / len(text)),
                f"...{text[start:end]}...",
            )
        else:
            return (0, text)

    def run(self, payload: dict, params: dict = None) -> dict:
        if "graph_process_pipe" in payload:
            graph = payload["graph_process_pipe"]["graph"]._graph
            query = params["query"]
            str_match_type = params["str_match_type"]
            str_lower = params["str_lower"]
            leafs = [node for node in graph.nodes if graph.nodes[node].get("payload")]
            leafs_contain_query = []
            for node in leafs:
                score, text = self.score_text_against_query(
                    graph.nodes[node]["payload"]["text"],
                    query,
                    str_match_type,
                    str_lower,
                )
                if score > 0:
                    leafs_contain_query.append([node, score, text])

            return {
                "anchor_nodes": sorted(
                    leafs_contain_query, key=lambda x: x[1], reverse=True
                )
            }
        else:
            raise Exception("You skipped graph_process_pipe !")
