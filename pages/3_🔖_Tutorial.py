import numpy as np
import os
import pandas as pd
import streamlit as st
import training as train

st.title("Evaluate effects of prices")

st.write("As a reminder, in the figure, you can see displayed the alternative configurations we will consider.")
st.write("AD is basic anaerobic digestion, ADCHP includes co-generation, ADU is membrane-based biogas upgrading, ADH2 is the methanation process.")

st.image("data/schematic.png")

with st.sidebar:
    st.sidebar.image("data/cooce_logo.png")
    st.write("Harnessing  potential of biogenic CO2 capture for Circular Economy")

if "capacity" not in st.session_state:
    st.session_state["capacity"] = 2700000

if "subsidies" not in st.session_state:
    st.session_state["subsidies"] = 0.5

st.write("These plants have as a common feature that they are capital-intensive compared to the potential profits they can make.")
st.write("To promote novel technologies governemnts can help regulating market prices.")
st.write("We will simulate the effect of a change in the regulation of markets that a governemnt can give.")

subsidies = st.session_state["subsidies"]
assets = train.Assets(st.session_state["capacity"])


prices = assets.calc_prices() * 1000
costs = assets.calc_fcosts() * 1000

input_dict = {  "CAPEX Subsidy": subsidies,
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


st.write("Remember that the simulations are valid for a plant capacity of ", assets.assets["capacity"].mean(), "cm / y")
st.write("Remember that the subsidy level is ", subsidies, "%.")

newprices = prices.copy(deep=True)
newcosts = costs.copy(deep=True)


st.write("Let's have a look at the main input parameters affecting the plants profitability, shown in the table below.")

my_table = st.table(inputs)

st.write("Let's have a look at the product prices affecting the plants profitability, shown in the table below.")
st.write("Prices are all in Euro/kWh, except for carbon dioxide, expressed in Euro / t.")

my_prices = st.data_editor(prices)

st.write("Let's have a look at the fuel costs affecting the plants profitability, shown in the table below.")
st.write("Costs are all in Euro/kWh, except for hydrogen, expressed in Euro / t.")
my_costs = st.data_editor(costs)

cflows, cumcflows, npv = assets.calc_npv(subsidies / 100, 
                                        inputs.iloc[1].values[0]/100,
                                        inputs.iloc[2].values[0]/100,
                                        inputs.iloc[3].values[0]/100, 
                                        inputs.iloc[4].values[0]/100, 
                                        inputs.iloc[5].values[0]/100, 
                                        inputs.iloc[6].values[0]/100, 
                                        my_prices,
                                        my_costs)


chart_table = cumcflows.transpose()


st.write("Let's check the plant profitability from the visualising the cumulative cash flows (k Euro/y) over time (years).")

st.line_chart(chart_table, use_container_width=True)



st.write("We can estimate the number of years to repay the initial investment, the so-called payback time.")
payback = assets.calc_payback(subsidies / 100, 
                                            inputs.iloc[1].values[0]/100,
                                            inputs.iloc[2].values[0]/100,
                                            inputs.iloc[3].values[0]/100, 
                                            inputs.iloc[4].values[0]/100, 
                                            inputs.iloc[5].values[0]/100, 
                                            inputs.iloc[6].values[0]/100,
                                            my_prices,
                                            my_costs)

chart_data = payback.transpose()
st.bar_chart(chart_data)
st.write("The chart displays the payback time in number of years necessary to recover from the initial investment for each technology, AD, ADCHP, ADU, ADH2.")

st.title("Exercise: next steps")

st.write("Change price of hydrogen from the table to check the effects on the profitability of the plant.")

st.write("Change the subsidisation level size to see the effects on the plant profitability.")

st.write("Change the capacity from the 'Tutorial n.1', to see a combined effect of size and subsidisation.")


