"""
adapted from GrandCypher  
GrandCypher is a Cypher interpreter for the Grand graph library.
source : https://github.com/aplbrain/grand-cypher/tree/master

"""

from cypherweb.core.node import Node
from rich import print as pprint

# from cypherweb.core.graph import Graph
# from typing import Dict, List, Callable, Tuple
import random
import string

# from functools import lru_cache
# import networkx as nx


# import grandiso

from lark import Lark, Transformer, v_args, Token


_AitoCypher = Lark(
    """
start               : query

query               : use_clause many_match_clause where_clause return_clause
                    | many_match_clause return_clause


many_match_clause   : (match_clause)+

use_clause          : "use"i ESTRING
match_clause        : "match"i node_match (edge_match node_match)*

where_clause        : "where"i compound_condition

compound_condition  : condition
                    | "(" compound_condition boolean_arithmetic compound_condition ")"
                    | compound_condition boolean_arithmetic compound_condition

condition           : entity_id op entity_id_or_value

?entity_id_or_value : entity_id
                    | value
                    | "NULL"i -> null
                    | "TRUE"i -> true
                    | "FALSE"i -> false

op                  : "==" -> op_eq
                    | "=" -> op_eq
                    | "<>" -> op_neq
                    | ">" -> op_gt
                    | "<" -> op_lt
                    | ">="-> op_gte
                    | "<="-> op_lte
                    | "is"i -> op_is
                    | "contains"i -> op_contains



return_clause       : "return"i entity_id ("," entity_id)*
                    | "return"i entity_id ("," entity_id)* limit_clause
                    | "return"i entity_id ("," entity_id)* skip_clause
                    | "return"i entity_id ("," entity_id)* skip_clause limit_clause

limit_clause        : "limit"i NUMBER
skip_clause         : "skip"i NUMBER


?entity_id          : CNAME
                    | CNAME "." CNAME

node_match          : "(" (CNAME)? (json_dict)? ")"
                    | "(" (CNAME)? ":" TYPE ("|" TYPE)* (json_dict)? ")"

edge_match          : LEFT_ANGLE? "--" RIGHT_ANGLE?
                    | LEFT_ANGLE? "-[]-" RIGHT_ANGLE?
                    | LEFT_ANGLE? "-[" CNAME "]-" RIGHT_ANGLE? 
                    | LEFT_ANGLE? "-[" CNAME ":" TYPE "]-" RIGHT_ANGLE? 
                    | LEFT_ANGLE? "-[" ":" TYPE "]-" RIGHT_ANGLE? 
                    | LEFT_ANGLE? "-[" "*" MIN_HOP "]-" RIGHT_ANGLE?
                    | LEFT_ANGLE? "-[" "*" MIN_HOP  ".." MAX_HOP "]-" RIGHT_ANGLE?
                    | LEFT_ANGLE? "-[" CNAME "*" MIN_HOP "]-" RIGHT_ANGLE?
                    | LEFT_ANGLE? "-[" CNAME "*" MIN_HOP  ".." MAX_HOP "]-" RIGHT_ANGLE?
                    | LEFT_ANGLE? "-[" ":" TYPE "*" MIN_HOP "]-" RIGHT_ANGLE?
                    | LEFT_ANGLE? "-[" ":" TYPE "*" MIN_HOP  ".." MAX_HOP "]-" RIGHT_ANGLE?
                    | LEFT_ANGLE? "-[" CNAME ":" TYPE "*" MIN_HOP "]-" RIGHT_ANGLE?
                    | LEFT_ANGLE? "-[" CNAME ":" TYPE "*" MIN_HOP  ".." MAX_HOP "]-" RIGHT_ANGLE?



LEFT_ANGLE          : "<"
RIGHT_ANGLE         : ">"
MIN_HOP             : INT
MAX_HOP             : INT
TYPE                : CNAME

json_dict           : "{" json_rule ("," json_rule)* "}"
?json_rule          : CNAME ":" value

boolean_arithmetic  : "and"i -> where_and
                    | "OR"i -> where_or

key                 : CNAME
?value              : ESTRING
                    | NUMBER
                    | "NULL"i -> null
                    | "TRUE"i -> true
                    | "FALSE"i -> false


%import common.CNAME            -> CNAME
%import common.ESCAPED_STRING   -> ESTRING
%import common.SIGNED_NUMBER    -> NUMBER
%import common.INT              -> INT

%import common.WS
%ignore WS

""",
    start="start",
)


_ALPHABET = string.ascii_lowercase + string.digits


def shortuuid(k=4) -> str:
    return "".join(random.choices(_ALPHABET, k=k))


class TreeToJson(Transformer):
    def __init__(self):
        self._return_requests = []
        self._limit = None
        self._skip = 0
        self.params = {
            "node_match": [],
            "edge_match": [],
            "where_clause": [],
            "return_clause": [],
        }

    null = lambda self, _: None
    true = lambda self, _: True
    false = lambda self, _: False
    ESTRING = v_args(inline=True)(eval)
    NUMBER = v_args(inline=True)(eval)

    def entity_id(self, entity_id):
        if len(entity_id) == 2:
            return ".".join(entity_id)
        return entity_id.value

    def op_eq(self, _):
        return "=="

    def op_neq(self, _):
        return "<>"

    def op_gt(self, _):
        return ">"

    def op_lt(self, _):
        return "<"

    def op_gte(self, _):
        return ">="

    def op_lte(self, _):
        return "<="

    def op_is(self, _):
        return "is"

    def op_contains(self, _):
        return "contains"

    def json_dict(self, tup):
        constraints = {}
        for key, value in tup:
            constraints[key] = value
        return constraints

    def json_rule(self, rule):
        return (rule[0].value, rule[1])

    def use_clause(self, use_clause):
        self.params["page_url"] = use_clause

    def node_match(self, node_name):
        cname = json_data = None
        node_types = []
        for token in node_name:
            if not isinstance(token, Token):
                json_data = token
            elif token.type == "CNAME":
                cname = token.value
            elif token.type == "TYPE":
                node_types.append(token.value)
        cname = cname or Token("CNAME", shortuuid())
        json_data = json_data or {}

        self.params["node_match"].append(
            {"node_name": cname, "node_type": node_types, "json_data": json_data}
        )
        pass

    def edge_match(self, edge_name):
        direction = cname = min_hop = max_hop = edge_type = None

        for token in edge_name:
            if token.type == "MIN_HOP":
                min_hop = int(token.value)
            elif token.type == "MAX_HOP":
                max_hop = int(token.value) + 1
            elif token.type == "LEFT_ANGLE":
                direction = "l"
            elif token.type == "RIGHT_ANGLE" and direction == "l":
                direction = "b"
            elif token.type == "RIGHT_ANGLE":
                direction = "r"
            elif token.type == "TYPE":
                edge_type = token.value
            else:
                cname = token.value

        direction = direction if direction is not None else "b"
        if (min_hop is not None or max_hop is not None) and (direction == "b"):
            raise TypeError("not support edge hopping for bidirectional edge")
        self.params["edge_match"].append(
            {
                "edge_name": cname,
                "edge_type": edge_type,
                "direction": direction,
                "min_hop": min_hop,
                "max_hop": max_hop,
            }
        )
        pass

    def where_and(self, val):
        self.params["where_clause"].append(
            {"entity_id": None, "operator": "AND", "value": None}
        )

    def where_or(self, val):
        self.params["where_clause"].append(
            {"entity_id": None, "operator": "OR", "value": None}
        )

    def condition(self, condition):
        if len(condition) == 3:
            (entity_id, operator, value) = condition
            self.params["where_clause"].append(
                {"entity_id": entity_id, "operator": operator, "value": value}
            )
            pass

    def limit_clause(self, limit):
        limit = int(limit[-1])
        self._limit = limit

    def skip_clause(self, skip):
        skip = int(skip[-1])
        self._skip = skip

    def return_clause(self, return_clause):
        for item in return_clause:
            if item:
                if not isinstance(item, str):
                    item = str(item.value)
                self._return_requests.append(item.value)
        self.params["return_clause"].append(
            {
                "return_requests": self._return_requests,
                "limit": self._limit,
                "skip": self._skip,
            }
        )
        pass

    def start(self, start):
        return self.params


class CypherApi(Node):
    def __init__(self) -> None:
        pass

    def populate_params(self, tree):
        """
        Populates the parameters of the function.

        Args:
            tree (dict): The tree containing the node match and where clause.

        Returns:
            dict: The dictionary containing the string matcher and graph nn.

        Raises:
            TypeError: If no node match is found.

        Notes:
            - This is a hard-coded parsing of the tree for now to be switched with a propper mmotif matching
            - If the node match is empty, a TypeError is raised.
            - If the node match has only one element, the node type is extracted and filter is applied on the node itself.
            - If the node match has multiple elements, we resolve to "ref_by_other_node" scenario.
        """
        node_match = tree["node_match"]
        where_clause = tree["where_clause"]
        if len(node_match) == 0:
            raise TypeError("no node match")
        if len(node_match) == 1:
            node_type = node_match[0]["node_type"]

            graph_nn = {
                "node_type": [t.lower() for t in node_type],
                "top_k_anchors": 10000,
                "top_k_neighbors": 10000,
                "node_include": len(where_clause) > 0,
            }
            str_matcher = {
                # "node_type": "title",
                "query": where_clause[0]["value"],
                "str_lower": True,
                "str_match_type": where_clause[0]["operator"],
            }
            return {
                "str_matcher": str_matcher,
                "graph_nn": graph_nn,
            }
        # node relation scenario
        node_type = node_match[0]["node_type"]
        edge_type = tree["edge_match"][0]
        graph_nn = {
            "node_type": [t.lower() for t in node_type],
            "top_k_anchors": 10000,
            "top_k_neighbors": 10000,
            "node_include": False,
        }
        str_matcher = {
            "node_type": [t.lower() for t in node_match[1]["node_type"]],
            "query": where_clause[0]["value"],  # should check on node type
            "str_lower": True,
            "str_match_type": where_clause[0]["operator"],
        }
        return {
            "str_matcher": str_matcher,
            "graph_nn": graph_nn,
        }

    def run(self, cypher_query: str, params: dict) -> dict:
        tree = _AitoCypher.parse(cypher_query)
        # pprint(tree)
        tree_payload = TreeToJson().transform(tree)
        # pprint(tree_payload)
        page_url = tree_payload["page_url"][0]
        _params = self.populate_params(tree_payload)
        pprint(_params)
        # _params = {
        #     "str_matcher": {
        #         "node_type": "title",
        #         "query": "trusted by",
        #         "str_lower": True,
        #         "str_match_type": "contains",
        #     },
        #     "graph_nn": {
        #         "node_type": "grid",
        #         "top_k_anchors": 10000,
        #         "top_k_neighbors": 10000,
        #         "node_include": False,
        #     },
        # }
        return {"page_url": page_url, "params": _params}
