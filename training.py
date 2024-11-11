import numpy as np
import os
import pandas as pd


class Assets:

    def __init__(self, capacity):
        # Alternative options include anaerobic digestion alone, anerobic digestion 
        # with CHP, anaerobic digestion with upgrade to biomethane, AD with CHP with upgrade
        technologies = ["AD", "ADCHP", "ADU", "ADH2"]
        data = np.array([capacity for i in range(len(technologies))])
        self.assets = pd.DataFrame(data=data, index=technologies, columns=["capacity"])

        # self.products = ["biogas", "biomethane"]
        # self.fuels = ["natural_gas", "electricity"]
        # self.emissions = ["CO2", "CH4"]
        self.yields = pd.DataFrame() # table
        self.lifetime = 40
        self.hours = 8660 # h/y
        self.utilisation_factor = 0.9 # fraction of hours for the plant to operate over a year
        self.LHV = 22 # lower heating value MJ/cm
        self.LHVkWh = 22 * 1000/ 3600 # lower heating value kWh/cm

    def calc_units(self):
        """These are the units for commodity flows"""
        quantities = ["biogas", "biomethane", "electricity", "heat", "CO2"]
        units = ["kWh/y", "kWh/y", "kWh/y", "kWh/y", "cm/y" ]
        return dict(zip(quantities,units))

    def cap2prod(self):
        """
        Conversion of units from original capacity units to production flow units
        biogas: from cm/y to kWh/y
        biomethane: from cm/y to kWh/y (36 MJ/cm as biomethane LHV)
        electricity: from cm/y to kWh/y
        heat: from cm/y to kWh/y
        CO2: from cm/y to cm/y
        """
        unit_converter = 0 * self.assets.copy()

        commodities = ["biogas", "biomethane", "electricity", "heat", "CO2", "H2", "feedstock"]
        
        unit_converter["biogas"] = self.LHVkWh / self.hours
        unit_converter["biomethane"] = 36 * 1000/(3600 * self.hours)
        unit_converter["electricity"] = self.LHVkWh / self.hours
        unit_converter["heat"] = self.LHVkWh  / self.hours
        unit_converter["CO2"] = 1 / self.hours      
        unit_converter["H2"] = 0  
        unit_converter["feedstock"] = 0  

        unit_converter = unit_converter.drop("capacity", axis=1)
        unit_converter = unit_converter[commodities]    
        return unit_converter

    def cap2cons(self):
        """
        Conversion of units from original capacity units to consumption flow units
        Consumption is calculated from biogas flow in cm/h
        biogas: from cm/y to cm/h
        biomethane: no conv
        electricity: no conv
        heat: no conv
        CO2: no conv
        """
        unit_converter = 0 * self.assets.copy()

        commodities = ["biogas", "biomethane", "electricity", "heat", "CO2", "H2", "feedstock"]

        unit_converter["biogas"] = 1 / self.hours
        unit_converter["biomethane"] = 1
        unit_converter["electricity"] = 1
        unit_converter["heat"] = 1
        unit_converter["CO2"] = 1   
        unit_converter["H2"] = 1     
        unit_converter["feedstock"] = 1

        unit_converter = unit_converter.drop("capacity", axis=1)
        unit_converter = unit_converter[commodities]
        return unit_converter


    def calc_capcosts(self, CO2split: float):
        """Returns capital costs in kEUR (2024)"""
        """Asset capacity is converted from cm/y into MW"""
        # biogas capex
        capacity = self.assets * self.LHV / self.hours / 3600
  
        capital_costs = 11202 * capacity**0.3486

        # biogas capex and CHP conversion
        ccAD = capital_costs.loc[capital_costs.index=="AD"].values
        capAD = capacity.loc[capacity.index=="AD"].values
        ccADCHP = ccAD + 1686.7 * capAD**0.7269
        ccADU = ccAD + 511.423 * capAD**0.6569

        capital_costs.loc[capital_costs.index=="AD"] = ccAD 
        capital_costs.loc[capital_costs.index=="ADCHP"] = ccADCHP
        # biogas capex and biomethane upgrade 
        # Techno-Economic Assessment of Biological Biogas Upgrading Based on Danish Biogas Plants (paper)
        capital_costs.loc[capital_costs.index=="ADU"] = ccADU

        capital_costs.loc[capital_costs.index=="ADH2"] = ccAD
        #assumption on scaling factor
        capADH2 = self.assets.loc[self.assets.index=="AD"].values*CO2split

        capital_costs.loc[capital_costs.index=="ADH2"] += 0.06 * (capADH2)**0.7 

        capital_costs.columns = ["capital_costs"]
        return capital_costs


    def calc_unitconsumption(self, CO2split: float):
        """Determine unit fuel consumption by technology"""
        """Values expressed in kWh/cm"""
        unitcons = 0 * self.assets.copy()

        commodities = ["biogas", "biomethane", "electricity", "heat", "CO2", "H2", "feedstock"]

        [unitcons.insert(loc=0, column=col, value=0) for col in commodities]
        unitcons = unitcons.drop("capacity", axis=1)
        
        capacity = self.assets.loc[self.assets.index=="AD"].values[0]
        # electricity consumption as a function of unitprod of biogas in cm/h
        # electricity in kWh / cm
        unitcons.loc[unitcons.index=="AD", "electricity"] = 8.18 
        unitcons.loc[unitcons.index=="AD", "electricity"]*= (self.utilisation_factor)**(-0.304) 
        unitcons.loc[unitcons.index=="AD", "electricity"]*= (capacity)**(-0.304)
        unitcons.loc[unitcons.index=="AD", "electricity"]*= (1/self.hours)**(-0.304)

        # heat estimated in kWh / cm (Giarola et al)
        # assuming heat consumption is half of electricity consumption
        unitcons.loc[unitcons.index=="AD", "heat"] = 0.5 * unitcons.loc[unitcons.index=="AD", "electricity"].values[0] 
        # this includes boiler efficiency and represents indeed ntural gas consumption
        unitcons.loc[unitcons.index=="AD", "heat"] = unitcons.loc[unitcons.index=="AD", "heat"]

        # electricity consumption as a function of production of biogas in cm
        # electricity in kWh / cm
        # Xiao Li's thesis
        capacity = self.assets.loc[self.assets.index=="ADCHP"].values[0]
        refvalue = unitcons.loc[unitcons.index=="AD", "electricity"].values[0]
        unitcons.loc[unitcons.index=="ADCHP", "electricity"] = refvalue + 0.13
        refvalue = unitcons.loc[unitcons.index=="AD", "heat"].values[0]
        unitcons.loc[unitcons.index=="ADCHP", "heat"] = refvalue

        # electricity consumption as a function of unitprod of biogas in cm/h
        # electricity in kWh / cm of biogas
        capacity = self.assets.loc[self.assets.index=="ADU"].values[0]
        topup = 0.0145 * (self.utilisation_factor / self.hours)**0.5627
        topup *= capacity**0.5627
        refvalue = unitcons.loc[unitcons.index=="AD", "electricity"].values[0]
        unitcons.loc[unitcons.index=="ADU", "electricity"] = refvalue + topup
        unitcons.loc[unitcons.index=="ADU", "heat"] = (1 + topup/refvalue) * unitcons.loc[unitcons.index=="AD", "heat"].values[0]
        #unitcons.loc[unitcons.index=="ADU", "biogas"] = 1

        # electricity consumption as a function of unitprod of biogas in cm/h
        # electricity in kWh / cm of biogas
        CO2density = 1.98 / 10**3 #t/cm Wikipedia
        methan_yield = 1.91 #0.353 CH4/CO2 initial https://www.sciencedirect.com/science/article/pii/S0016236123013923
        capacity = self.assets.loc[self.assets.index=="ADH2"].values[0]
        refvalue = unitcons.loc[unitcons.index=="ADU", "electricity"].values[0] 
        refcapacity =  methan_yield / CO2density / CO2split
        unitcons.loc[unitcons.index=="ADH2", "heat"] = refvalue + 2.42 / refcapacity
        unitcons.loc[unitcons.index=="ADH2", "electricity"] = refvalue

        # H2 in t defined from cm/h
        refcapacity = CO2split * CO2density  
        unitcons.loc[unitcons.index=="ADH2", "CO2"] = refcapacity
        unitcons.loc[unitcons.index=="ADH2", "H2"] = 0.15 * refcapacity
        #unitcons.loc[unitcons.index=="ADH2", "biogas"] = 1

        # feedstock kWh consumption as a function of unitprod of biogas in cm       
        unitcons["feedstock"] = 0.05

        unitcons = unitcons[commodities]
        return unitcons


    def calc_unitproduction(self, CO2split: float, biometyield:float, heatgen: float, elecgen: float):
        """Determine unit fuel consumption by technology
        receives:
        CO2split: fraction by volume of CO2
        biometyield: yield to biomethane from biogas
        heatgen: thermal CHP efficiency
        elecgen: electrical CHP efficiency"""

        unitprod = 0 * pd.DataFrame().reindex_like(self.assets)
        commodities = ["biogas", "biomethane", "electricity", "heat", "CO2", "H2", "feedstock"]

        [unitprod.insert(loc=0, column=col, value=0) for col in commodities]
        unitprod = unitprod.drop("capacity", axis=1)
        unitprod = unitprod[commodities]
        # electricity consumption as a function of production of biogas in cm/h
        # electricity in kWhoutput / kWinput
        unitprod.loc[unitprod.index=="AD", "biogas"] = 0 #1 
        unitprod.loc[unitprod.index=="AD", "heat"] = 0.85
        unitprod.loc[unitprod.index=="ADCHP", "heat"] = heatgen
        unitprod.loc[unitprod.index=="ADCHP", "electricity"] = elecgen

        # asset capacity is in cm/y
        # biomethane is obtained considering a volume-based yield cm of CH4 / cm

        unitprod.loc[unitprod.index=="ADU", "biomethane"] =  biometyield * (1- CO2split)
        # CO2 in t
        CO2density = 1.98 / 1000 # density in t/m3
        unitprod.loc[unitprod.index=="ADU", "CO2"] =  (1 - biometyield ) * CO2density

        # ADH2 works as ADU but with H2
        # https://www.sciencedirect.com/science/article/pii/S0016236123013923
        methan_conv = 0.98
        biometh_density = 0.75 / 1000 # t / m3
        refvalue = unitprod.loc[unitprod.index=="ADU", "biomethane"].values[0] # cm CH4 / cm
        topup = 0.353 * CO2split * CO2density / biometh_density 
        unitprod.loc[unitprod.index=="ADH2", "biomethane"] = refvalue + topup
        unitprod.loc[unitprod.index=="ADH2", "CO2"] = (1 - biometyield ) * CO2density

        unitprod = unitprod[commodities]
        return unitprod

    def calc_production(self,CO2split: float, biometyield: float, heatgen: float, elecgen: float):
        """Determine production by technology
        receives:
        CO2split: fraction by volume of CO2
        biometyield: yield to biomethane from biogas
        heatgen: thermal CHP efficiency
        elecgen: electrical CHP efficiency"""

        unit_converter = self.cap2prod()     
        
        outputs = self.calc_unitproduction(CO2split, biometyield, heatgen, elecgen)

        production = pd.concat([outputs[col] * self.assets.capacity for col in outputs.columns], axis=1)

        production.columns = outputs.columns #rename columns

        production *= self.utilisation_factor

        production = pd.concat([production[col] * unit_converter[col] for col in outputs.columns], axis=1)

        return production * self.hours

    def calc_consumption(self, CO2split: float, biometyield: float, heatgen: float, elecgen: float):
        """Determine consumption by technology
        receives:
        CO2split: fraction by volume of CO2 (cm/y)
        biometyield: yield to biomethane from biogas (kwh/y)
        heatgen: thermal CHP efficiency (kwh/y)
        elecgen: electrical CHP efficiency (kwh/y)"""   

        unit_converter = self.cap2cons()   

        fuels = self.calc_unitconsumption(CO2split)

        consumption = pd.concat([fuels[col] * self.assets.capacity for col in fuels.columns], axis=1)

        consumption.columns = fuels.columns #rename columns

        consumption *= self.utilisation_factor

        # Divide by self.hours
        consumption = pd.concat([consumption[col] * unit_converter['biogas'].values[0] for col in fuels.columns], axis=1)
        
        consumption.columns = fuels.columns #rename columns  
        
        # Multiply by self.hours to get annual quanitites (analogy with production)
        return consumption * self.hours

    def calc_prices(self):
        """Estimate prices"""
        prices = 0 * pd.DataFrame().reindex_like(self.assets)
        commodities = ["biogas", "biomethane", "electricity", "heat", "CO2", "H2", "feedstock"]

        [prices.insert(loc=0, column=col, value=0) for col in commodities]

        prices.loc["AD", "biogas"] = 0.0  #euro / kWh
        prices.loc["AD", "electricity"] = 0.044  #euro / kWh
        prices["biomethane"] = 0.05  #euro / kWh
        prices.loc["ADU", "electricity"] = 0.044  #euro / kWh
        prices.loc["ADCHP", "electricity"] = 0.54 #euro / kWh
        prices.loc["ADH2", "electricity"] = 0.044 #euro / kWh
        #https://www.statista.com/statistics/1047083/natural-gas-price-european-union-country/
        prices["heat"] = 0
        prices["feedstock"] = 0 #euro/kWh
        prices["H2"] = 0 #euro/t
        prices.loc["ADH2", "CO2"] = 0 #euro/t
        prices = prices.drop("capacity", axis=1)

        prices = prices[commodities] / 1000# keuro / kWh
        return prices 

    def calc_fcosts(self):
        """Estimate costs
        Samme as prices but distinguishes for autoproducers"""
        prices = 0 * pd.DataFrame().reindex_like(self.assets)
        commodities = ["biogas", "biomethane", "electricity", "heat", "CO2", "H2", "feedstock"]

        [prices.insert(loc=0, column=col, value=0) for col in commodities]

        prices.loc["AD", "biogas"] = 0.0  #euro / kWh
        prices.loc["AD", "electricity"] = 0.044  #euro / kWh
        prices.loc["ADCHP", "electricity"] = 0.044  #euro / kWh
        prices.loc["ADU", "electricity"] = 0.044  #euro / kWh
        prices.loc["ADH2", "electricity"] = 0.044  #euro / kWh
        prices["biomethane"] = 0.0  #euro / kWh
        #https://www.statista.com/statistics/1047083/natural-gas-price-european-union-country/
        prices["heat"] = 0.06
        prices["feedstock"] = -20 #euro/kWh
        prices["H2"] = 3000 #euro/t
        prices["ADH2", "CO2"] = 0 #euro/t
        prices = prices.drop("capacity", axis=1)

        prices = prices[commodities] / 1000# keuro / kWh
        return prices 

    
    def calc_updtprices(self, newprices: pd.DataFrame):
        """Receives new prices from users"""
        return newprices
    

    def calc_revenues (self, 
                       CO2split: float, 
                       biometyield: float, 
                       heatgen: float, 
                       elecgen: float,
                       newprices: pd.DataFrame):

        if newprices.sum().sum() > 0:
            prices = newprices / 1000
        else:
            prices = self.calc_prices()
        prices = self.calc_prices()
        production = self.calc_production(CO2split, biometyield, heatgen, elecgen)
        revenues = production * prices
        commodities = ["biogas", "biomethane", "electricity", "heat", "CO2", "H2", "feedstock"]
        revenues = revenues[commodities]
        return revenues


    def calc_costs(self, 
                   capsubsidy: float,
                   CO2split: float):
        """Determine unit fuel consumption by technology
        Check IEA-ETSAP sources"""

        capital_costs = self.calc_capsub(capsubsidy, CO2split)
        fixom = 0.1 * capital_costs
        virom = 0.05 * capital_costs #estimate
        return fixom + virom

    def calc_fuelcosts(self,
                       CO2split: float, 
                       biometyield: float, 
                       heatgen: float, 
                       elecgen: float,
                       newcosts: pd.DataFrame):
        if newcosts.sum().sum() > 0:
            costs = newcosts / 1000
        else:
            costs = self.calc_fcosts()

        consumption = self.calc_consumption(CO2split, biometyield, heatgen, elecgen)
        fuel_costs = consumption * costs

        return fuel_costs

        

    def calc_amort(self, capsubsidy: float, CO2split: float):
        capital_costs = self.calc_capsub(capsubsidy, CO2split)
        amortization = 0.2 * capital_costs
        return amortization


    def calc_capsub(self, capsubsidy: float, CO2split: float):
        """Calculates an incentive on the capital costs"""
        capital_costs = self.calc_capcosts(CO2split)
        capital_costs *= (1- capsubsidy)
        return capital_costs

    def calc_cf_wam (self, 
                    capsubsidy: float, 
                    taxrate: float, 
                    CO2split: float, 
                    biometyield: float, 
                    heatgen: float, 
                    elecgen: float,
                    newprices: pd.DataFrame,
                    newcosts: pd.DataFrame):
        """Cash flows with amortization"""
        fixed_costs = self.calc_costs(capsubsidy, CO2split)
        revenues = self.calc_revenues(CO2split, biometyield, heatgen, elecgen, newprices)
        fuel_costs = self.calc_fuelcosts(CO2split, biometyield, heatgen, elecgen, newcosts)
        amortization = self.calc_amort(capsubsidy, CO2split)
        cflows = revenues.sum(axis=1) - fixed_costs.sum(axis=1) - fuel_costs.sum(axis=1)- amortization.sum(axis=1)
        if np.all(cflows.values > 0):
            cflows = cflows * (1 - taxrate)
        cflows += amortization.sum(axis=1)
        return cflows

    def calc_cf_woam(self,
                    capsubsidy: float, 
                    taxrate: float, 
                    CO2split: float, 
                    biometyield: float, 
                    heatgen: float, 
                    elecgen: float,
                    newprices: pd.DataFrame,
                    newcosts: pd.DataFrame):
        """Cash flows without amortization"""
        fixed_costs = self.calc_costs(capsubsidy, CO2split)
        revenues = self.calc_revenues(CO2split, biometyield, heatgen, elecgen, newprices)
        fuel_costs = self.calc_fuelcosts(CO2split, biometyield, heatgen, elecgen, newcosts)        
        cflows = revenues.sum(axis=1) - fixed_costs.sum(axis=1) - fuel_costs.sum(axis=1)
        if np.all(cflows.values > 0):
            cflows = cflows * (1 - taxrate)

        return cflows

    def calc_rates(self, drate: float, start: int, stop: int):
        return [1/(1 + drate)**i for i in np.arange(start, stop + 1, 1)]

    def calc_npv(self,
                 capsubsidy: float, 
                 drate: float, #discount rate
                 taxrate: float, 
                 CO2split: float, 
                 biometyield: float, 
                 heatgen: float, 
                 elecgen: float,
                 newprices: pd.DataFrame,
                 newcosts: pd.DataFrame):

        capital_costs = self.calc_capsub(capsubsidy, CO2split)
        npv = - capital_costs.sum(axis=1)
        technologies = ["AD",	"ADCHP", "ADU",	"ADH2"]

        cflows = self.calc_cf_wam(capsubsidy, taxrate, CO2split, biometyield, heatgen, elecgen, newprices, newcosts)

        rates = self.calc_rates(drate, 1, 5)
        allcf1 = pd.DataFrame(np.array([cflows * rates[i] for i in range(len(rates))]).transpose())
        allcf1.columns = list(np.arange(1, 6, 1))
        rates = self.calc_rates(drate, 6, self.lifetime)
        cflows = self.calc_cf_woam(capsubsidy, taxrate, CO2split, biometyield, heatgen, elecgen, newprices, newcosts)

        allcf2 = pd.DataFrame(np.array([cflows * rates[i] for i in range(len(rates))]).transpose())
        allcf2.columns = list(np.arange(6, self.lifetime + 1, 1))

        allcf = pd.concat((allcf1, allcf2), axis=1)

        npv.index = [0,1,2,3]

        allcf = pd.concat((npv, allcf), axis=1)

        allcf.index = technologies
        
        allcfcum = allcf.cumsum(axis=1)

        npv = allcfcum[20]
        return allcf, allcfcum, npv

    def calc_payback(self,
                    capsubsidy: float, 
                    drate: float, #discount rate
                    taxrate: float, 
                    CO2split: float, 
                    biometyield: float, 
                    heatgen: float, 
                    elecgen: float,
                    newprices: pd.DataFrame,
                    newcosts: pd.DataFrame):

        allcf, allcfcum, npv = self.calc_npv(capsubsidy,
                                             drate,
                                             taxrate, 
                                             CO2split, 
                                             biometyield, 
                                             heatgen, 
                                             elecgen,
                                             newprices,
                                             newcosts)
        capital_costs = self.calc_capsub(capsubsidy, CO2split)
        npv = - capital_costs.sum(axis=1)
        technologies = ["AD",	"ADCHP", "ADU",	"ADH2"]

        cflows = self.calc_cf_wam(capsubsidy, taxrate, CO2split, biometyield, heatgen, elecgen, newprices, newcosts)

        rates = self.calc_rates(drate, 1, 5)
        allcf1 = pd.DataFrame(np.array([cflows * rates[i] for i in range(len(rates))]).transpose())
        allcf1.columns = list(np.arange(1, 6, 1))
        rates = self.calc_rates(drate, 6, self.lifetime)
        cflows = self.calc_cf_woam(capsubsidy, taxrate, CO2split, biometyield, heatgen, elecgen, newprices, newcosts)

        allcf2 = pd.DataFrame(np.array([cflows * rates[i] for i in range(len(rates))]).transpose())
        allcf2.columns = list(np.arange(6, self.lifetime + 1, 1))

        allcf = pd.concat((allcf1, allcf2), axis=1)

        npv.index = [0,1,2,3]

        allcf = pd.concat((npv, allcf), axis=1)

        allcf.index = technologies
        
        allcfcum = allcf.cumsum(axis=1)

        npv = allcfcum[20]

        columns = list(np.arange(6, 20,1))

        return capital_costs["capital_costs"] /allcf[columns].mean(axis=1)