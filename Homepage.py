import numpy as np
import os
import pandas as pd
import streamlit as st
#import import_ipynb
import training as train

st.set_page_config(page_title="Welcome", page_icon="✋🏼")
st.title("Harnessing  potential of biogenic CO2 capture for Circular Economy")

# add_selectbox = st.sidebar.selectbox(
#     "How would you like to be contacted?",
#     ("Email", "Home phone", "Mobile phone")
# )

url ="https://www.imperial.ac.uk/"
with st.sidebar:
    st.write("Welcome to the CooCE project!")
    st.sidebar.image("data/cooce_logo.png")
    st.write("\n")
    st.write("\n")
    st.write("This application can help assess options to valorise biogas")
    st.markdown("It has been realised by Dr. Sara Giarola, from [Imperial College London](https://www.imperial.ac.uk/)")
    st.markdown("Contacts: s.giarola10@imperial.ac.uk (Sara Giarola), r.diaz-chavez@imperial.ac.uk (Rocio Diaz-Chavez)")
    st.sidebar.image("data/Imperial_logo.png")





st.title("")

st.write("CooCE is a EU-funded project")
st.image("data/homepage.png")


st.write("In this tutorial, we will focus on the possible options to valorise biogas.", "\n")
st.write("The biogas streams produced at a waste water treatment plant are usually burned to generate heat.", "\n")
st.write("The possible options which will be the focus of this tutorial include the use of biogas for co-generation and the production of biomethane")

st.write("\n", "\n")







