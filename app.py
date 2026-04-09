import streamlit as st
import pandas as pd
import altair as alt
import re
from collections import defaultdict

st.set_page_config(page_title="LaunchX Entrepreneurial Readiness", layout="wide", initial_sidebar_state="collapsed")

# Hide Streamlit's default menu, footer, and header
hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = 0
if "scene_step" not in st.session_state:
    st.session_state.scene_step = 0
if "scene_choices" not in st.session_state:
    st.session_state.scene_choices = {}
if "self_assess" not in st.session_state:
    st.session_state.self_assess = {f"slider_{i}": 5 for i in range(8)}
if "reflections" not in st.session_state:
    st.session_state.reflections = {"motivation": "", "failure": "", "vision": ""}
if "email" not in st.session_state:
    st.session_state.email = ""
if "name" not in st.session_state:
    st.session_state.name = ""
if "results" not in st.session_state:
    st.session_state.results = None
