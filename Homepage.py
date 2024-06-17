import numpy as np
import os
import pandas as pd
import streamlit as st
import import_ipynb
import training as train

st.set_page_config(page_title="Welcome", page_icon="✋🏼")
st.title("Harnessing  potential of biogenic CO2 capture for Circular Economy")

# add_selectbox = st.sidebar.selectbox(
#     "How would you like to be contacted?",
#     ("Email", "Home phone", "Mobile phone")
# )


with st.sidebar:
    st.sidebar.image("/Users/sara/trainingCooCE/data/cooce_logo.png")
    add_name = st.text_input("Enter your name", "sara")
    st.write("Welcome ", add_name, ", to the CooCE project!")
    st.write("We will assess the possible options to valorise biogas.")





st.title("")

st.write("CooCE is a EU-funded project")
st.image("/Users/sara/trainingCooCE/data/homepage.png")


st.write("In this tutorial, we will focus on the possible options to valorise biogas.", "\n")
st.write("The biogas streams produced at a waste water treatment plant are usually burned to generate heat.", "\n")
st.write("The possible options which will be the focus of this tutorial include the use of biogas for co-generation and the production of biomethane")

st.write("\n", "\n")







