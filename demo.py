"""
# My first app
Here's our first attempt at using data to create a table:
"""
import subprocess
import sys


def install(package):
    subprocess.run(["pip", "install", package])


try:
    from cypherweb.pipelines import CypherWebPipeline
except:
    install("git+https://github.com/AnasAito/cypher-web")
    from cypherweb.pipelines import CypherWebPipeline


import streamlit as st
import streamlit_javascript as st_js
from streamlit_ace import st_ace
import streamlit.components.v1 as components
from cypherweb.pipelines import CypherWebPipeline
from cypherweb.utils.visualizations import render_element_from_root

st.set_page_config(page_title="CypherWeb Demo", page_icon="🎈", layout="wide")
st.title("CypherWeb Demo")
ui_width = st_js.st_javascript("window.innerWidth")
# st.write(ui_width)
cypher_query = """
USE "https://weaviate.io/company/about-us"
MATCH (a:Grid)-[e*1..2]->(t:Title)
WHERE t.text contains "team"
RETURN a, t
"""
if "page_url" not in st.session_state:
    st.session_state["page_url"] = "https://weaviate.io/company/about-us"
# col3, col4 = st.columns([3 if ui_width > 1400 else 4, 9])
col3, col4 = st.tabs(
    [
        "Cypher playground",
        "Web page",
    ]
)
with col3:
    query = st_ace(
        value=cypher_query,
        language="sql",
        theme="twilight",
        auto_update=False,
        font_size=20,
    )
with col4:
    components.iframe(st.session_state.page_url, height=600, scrolling=True)
if "match" in query.lower():
    pipe = CypherWebPipeline()
    results = pipe.run(query)
    st.session_state.page_url = results["_start"]["page_url"]
# print(query)
# print(results)
# Create a single-line code input
# code_input = st.code(query, language="cypher")
# Create a single-line code input

# col1, col2 = st.columns(2)
col1, col2 = st.tabs(
    [
        "Results",
        "(String) Visualize result",
    ]
)
with col1:
    st.write(results)
with col2:
    str_agg = ""
    with st.form(key="my_form"):
        element_id = st.text_input(label="Enter element ID")
        submit_button = st.form_submit_button(label="Submit")
    element_id = element_id.replace('"', "").strip()
    graph = pipe.graph._graph
    try:
        str_agg = render_element_from_root(graph, element_id, depth=0, str_agg=str_agg)
        print("to be written", str_agg)
        st.code(str_agg, language="python")
    except Exception as e:
        # st.write(e)
        st.write("Error while rendering element (check your element id)")
