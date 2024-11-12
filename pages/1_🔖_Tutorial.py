import numpy as np
import os
import pandas as pd
import streamlit as st
import training as train

st.title("Choose a plant capacity")

st.write("In the figure, you can see displayed the alternative configurations we will consider.")
st.write("AD represents the basic configuration, using anaerobic digestion in a wastewater treatment plant.")
st.write("The biogas produced is burned for fulling heating needs of the plant.")
st.write("ADCHP is a configuration where biogas is used in a co-generation system for heat and power generation.")
st.write("The biogas upgrading to biomethane is modelled in two ways.")
st.write("Existing systems use membrane separation for purifying the methane stream (AD).")
st.write("A second way uses methanation where hydrogen is used to convert carbon dioxide into methane (ADH2).")

st.image("data/schematic.png")

with st.sidebar:
    st.sidebar.image("data/cooce_logo.png")
    st.write("Harnessing  potential of biogenic CO2 capture for Circular Economy")
    st.write("\n")
    st.write("\n")
    st.write("This application can help assess options to valorise biogas")
    st.markdown("Designed by Dr. Sara Giarola", "\n", "Co-designed by Dr. Rocio Diaz-Chavez")
    st.markdown("From [Imperial College London](https://www.imperial.ac.uk/)")
    st.markdown("Contacts: Dr. Sara Giarola (s.giarola10@imperial.ac.uk), Dr. Rocio Diaz-Chavez (r.diaz-chavez@imperial.ac.uk)")
    st.sidebar.image("data/Imperial_logo.png")
    
if "capacity" not in st.session_state:
    st.session_state["capacity"] = 2700000


capacity = st.radio(
    "Choose a capacity for the plant in cm / y",
    (1000000, 2700000, 5400000, 10800000)
)

newprices = 0 * pd.DataFrame()
newcosts = 0 * pd.DataFrame()

input_dict = {  "CAPEX Subsidy": 0.5,
                "Dicount rate": 0.05,
                "Taxation rate": 0.36,
                "CO2 vol. perc. in biogas": 0.4,
                "Biomethane yield": 0.48,
                "CHP Thermal efficiency": 0.60,
                "CHP electrical efficiency": 0.28
                }

descriptors = ["Reduction in capital costs (perc.)",
               "Value of time applied to future cash flows (perc.)",
               "Apportioning of revenues going into taxes (perc.)",
               "CO2 by volume in biogas (perc.)",
               "Yield of biomethane from biogas (perc.)",
               "Heat production from biogas in CHP (perc.)",
               "Electricity production from biogas in CHP (perc.)"]

data = np.array([value *100 for value in input_dict.values()]).reshape(1,-1).transpose()
inputs = pd.DataFrame(data, index=descriptors, columns=["Data input"])

submit = st.button("Submit")
if submit:
    st.session_state["capacity"] = capacity
    st.write("The updated plant size is ", capacity, "cm / y")


assets = train.Assets(capacity)

cflows, cumcflows, npv = assets.calc_npv(inputs.iloc[0].values[0]/100, 
                                        inputs.iloc[1].values[0]/100,
                                        inputs.iloc[2].values[0]/100,
                                        inputs.iloc[3].values[0]/100, 
                                        inputs.iloc[4].values[0]/100, 
                                        inputs.iloc[5].values[0]/100, 
                                        inputs.iloc[6].values[0]/100, 
                                        newprices,
                                        newcosts    )

st.write("Let's have a look at the main input parameters affecting the plants profitability, shown in the table below.")

my_table = st.table(inputs)

chart_table = cumcflows.transpose()

st.title("Cash flows")
st.write("Let's check the plant profitability from the visualising the cumulative cash flows (k Euro/y) over time (years).")

st.line_chart(chart_table, use_container_width=True)


st.title("Payback time")
st.write("We can estimate the number of years to repay the initial investment, the so-called payback time.")
payback = assets.calc_payback(inputs.iloc[0].values[0]/100, 
                                            inputs.iloc[1].values[0]/100,
                                            inputs.iloc[2].values[0]/100,
                                            inputs.iloc[3].values[0]/100, 
                                            inputs.iloc[4].values[0]/100, 
                                            inputs.iloc[5].values[0]/100, 
                                            inputs.iloc[6].values[0]/100, 
                                            newprices,
                                            newcosts    )

chart_data = payback.transpose()
st.bar_chart(chart_data)
st.write("The chart displays the payback time in number of years necessary to recover from the initial investment for each technology, AD, ADCHP, ADU, ADH2.")

st.title("Exercise")
st.write("Change the capacity size to see the effects on the plant profitability, looking at cash flows and payback time.")

