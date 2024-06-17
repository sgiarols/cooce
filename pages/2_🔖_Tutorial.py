import numpy as np
import os
import pandas as pd
import streamlit as st
import training as train

st.title("Choose subsidisation")

st.write("As a reminder, in the figure, you can see displayed the alternative configurations we will consider.")
st.write("AD is basic anaerobic digestion, ADCHP includes co-generation, ADU is membrane-based biogas upgrading, ADH2 is the methanation process.")

st.image("data/schematic.png")

with st.sidebar:
    st.sidebar.image("data/cooce_logo.png")
    st.write("Harnessing  potential of biogenic CO2 capture for Circular Economy")

if "capacity" not in st.session_state:
    st.session_state["capacity"] = 2700000

if "subsidies" not in st.session_state:
    st.session_state["subsidies"] = 0.1

st.write("These plants have as a common feature that they are capital-intensive compared to the potential profits they can make.")
st.write("To promote novel technologies governemnts can help facing the upfront costs.")
st.write("We will simulate the effect of a change in the level of contribution that a governemnt can give.")


subsidies = st.radio(
    "Choose a subsidy level for the plant, as a percentage of the upfront cost (capital costs) that the governemnt can support",
    (0, 10, 30, 50, 70, 90)
)

newprices = 0 * pd.DataFrame()
newcosts = 0 * pd.DataFrame()

input_dict = {  "CAPEX Subsidy": subsidies / 100,
                "Dicount rate": 0.1,
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
    st.session_state["subsidies"] = subsidies
    st.write("The updated subsidy level is ", subsidies, "%")


assets = train.Assets(st.session_state["capacity"])

st.write("Remember that the simulations are valid for a plant capacity of ", assets.assets["capacity"].mean(), "cm / y")

cflows, cumcflows, npv = assets.calc_npv(inputs.iloc[0].values[0]/100, 
                                        inputs.iloc[1].values[0]/100,
                                        inputs.iloc[2].values[0]/100,
                                        inputs.iloc[3].values[0]/100, 
                                        inputs.iloc[4].values[0]/100, 
                                        inputs.iloc[5].values[0]/100, 
                                        inputs.iloc[6].values[0]/100,
                                        newprices,
                                        newcosts )

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
                                            newcosts)

chart_data = payback.transpose()
st.bar_chart(chart_data)
st.write("The chart displays the payback time in number of years necessary to recover from the initial investment for each technology, AD, ADCHP, ADU, ADH2.")

st.title("Exercise")
st.write("Change the subsidisation level size to see the effects on the plant profitability, looking at cash flows and payback time.")

st.write("Change the capacity from the 'Tutorial n.1', to see a combined effect of size and subsidisation.")


