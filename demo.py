"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
from streamlit_ace import st_ace
from cypherweb.pipelines import CypherWebPipeline
from cypherweb.utils.visualizations import render_element_from_root

st.set_page_config(page_title="CypherWeb Demo", page_icon="🎈", layout="wide")
st.title("CypherWeb Demo")
cypher_query = """
USE "https://www.wiz.io/"
MATCH (a:Grid)-[e*1..2]->(t:Title)
WHERE t.text contains "risks"
RETURN a, t
"""
# code_input = st.text_area(cypher_query, height=200)
# Spawn a new Ace editor
query = st_ace(value=cypher_query, language="sql", theme="twilight", auto_update=False)
if "match" in query.lower():
    pipe = CypherWebPipeline()
    results = pipe.run(query)
# print(query)
# print(results)
# Create a single-line code input
# code_input = st.code(query, language="cypher")
# Create a single-line code input

col1, col2 = st.columns(2)
with col1:
    st.write(results)
with col2:
    str_agg = ""
    element_id = st.text_input("element_id").replace('"', "").strip()
    graph = pipe.graph._graph
    str_agg = render_element_from_root(graph, element_id, depth=0, str_agg=str_agg)
    print("to be written", str_agg)
    st.code(str_agg, language="python")
