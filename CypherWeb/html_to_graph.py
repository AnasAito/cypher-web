import networkx as nx
import re


NOT_PERMITED_TAGS = [
    "script",
    "img",
    "noscript",
    "svg",
    "input",
    "style",
    "kin-address-form",
    "picture",
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


def has_payload(element):
    """
    only capture payload if element is leaf
    """
    if isinstance(
        element, str
    ):  # hot fix for ('NavigableString' object has no attribute 'contents')
        return True
    return len(element.contents) == 1 and len(element.text.strip()) > 2


def format_text(text):
    text = text.replace("\n", " ").strip()
    return " ".join(re.split("\s+", text, flags=re.UNICODE)).strip()


def get_payload(node):
    if isinstance(node, str):
        return {"href": None, "text": format_text(node.text)}
    return {"href": node.get("href", None), "text": format_text(node.text)}


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
    _soup, _graph: nx.Graph, _counter, global_counter, _parent=None
) -> None:
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
            node_id = _element_name  # hash name

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
                                "class": "_CLASSJOIN_".join(element_class),
                                "payload": payload,
                            },
                        )
                    ]
                )

                global_counter += 1
                _graph.add_edge(_parent, node_id)

            _counter[element_name] += 1
            if not element_name == "p":
                traverse_html(
                    element_content, _graph, _counter, global_counter, node_id
                )
