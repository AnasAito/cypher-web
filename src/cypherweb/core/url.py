# Url datat structure
from dataclasses import dataclass


@dataclass
class Url:
    page_url: str
    depth: int
    enrich_inner_urls: bool = False
