import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd
import pydeck as pdk
from plotly.tools import mpl_to_plotly
import re
import numpy as np
import random
import shapely


st.set_page_config(layout="wide")

# Load the geopackage file
#df = pd.read_csv("test_df_bt.csv")
df_prob = pd.read_csv("df_prob_smart.csv", index_col = 0)

df = pd.read_excel("Data/Data Sander.xlsx")
sndr = pd.read_excel("Data/Data Sander.xlsx")
vrtg_verdeling = pd.read_csv("Data/Motorvoertuigen__type__postcode__regio_s_14042023_154158 (1).csv", sep = ";")
vrtg_verdeling = vrtg_verdeling[vrtg_verdeling["Perioden"] == 2022]
panden = gpd.read_file("Data/pand 1681 2133.gpkg")

df = df[df["Bedrijventerrein"]=="STP"]
sndr = sndr[sndr["Bedrijventerrein"]=="STP"]

#postcodes van sanders data krijgen
split_data = sndr["Adres"].str.split(", ", n=1, expand=True)
sndr["straat"] = split_data[0]
sndr["plaats"] = split_data[1]
sndr["pc4"] = sndr["plaats"].str.extract('(\d+)').astype(float)
sndr_pc = sndr[sndr["pc4"].notna()]
sndr_pc["pc4"] = sndr_pc["pc4"].astype('int')

panden = panden[["gebruiksdoel", "oppervlakte", "openbare_ruimte", "huisnummer", "huisletter", "postcode", "geometry"]]
panden["pc4"] = panden["postcode"].str.extract('(\d+)', expand=False)
panden = panden.fillna("")
panden["huisletter"] = panden["huisletter"].str.lower()
panden["straat"] = panden["openbare_ruimte"] + str(" ") + panden["huisnummer"].astype(str) + panden["huisletter"]
#toevoegen samenvoeging Groothandelsmarkt 8-10
g8 = panden[panden["straat"].isin(["Groothandelsmarkt 8", "Groothandelsmarkt 10"])].groupby("openbare_ruimte")["oppervlakte"].sum().iloc[0]
g8_10 = panden[panden["straat"] == "Groothandelsmarkt 10"]
g8_10["oppervlakte"] = g8
g8_10["huisnummer"] = "8-10"
g8_10["straat"] = ["Groothandelsmarkt 8-10"]
panden = pd.concat([panden, g8_10])

sndr = sndr.merge(panden, on = "straat", how = "left")
verdeling = sndr[['Bedrijf', 'pc4_y', 'oppervlakte']]

verdeling = verdeling.rename(columns = {"pc4_y":"pc4"})

verdeling["totaal oppervlakte"] = verdeling["oppervlakte"].sum()

#Eigen voertuig aantallen
vrtg_verdeling = vrtg_verdeling[["Regio's", 'Wegvoertuigen per 1 januari/Bedrijfsvoertuigen/Totaal bedrijfsvoertuigen (aantal)',
       'Wegvoertuigen per 1 januari/Bedrijfsvoertuigen/Bedrijfsmotorvoertuigen/Totaal bedrijfsmotorvoertuigen (aantal)',
       'Wegvoertuigen per 1 januari/Bedrijfsvoertuigen/Bedrijfsmotorvoertuigen/Bestelauto (aantal)',
       'Wegvoertuigen per 1 januari/Bedrijfsvoertuigen/Bedrijfsmotorvoertuigen/Vrachtauto (excl. trekker voor oplegger) (aantal)',
       'Wegvoertuigen per 1 januari/Bedrijfsvoertuigen/Bedrijfsmotorvoertuigen/Trekker voor oplegger (aantal)',
       'Wegvoertuigen per 1 januari/Bedrijfsvoertuigen/Bedrijfsmotorvoertuigen/Speciaal voertuig (aantal)',
       'Wegvoertuigen per 1 januari/Bedrijfsvoertuigen/Bedrijfsmotorvoertuigen/Bus (aantal)',
       'Wegvoertuigen per 1 januari/Bedrijfsvoertuigen/Aanhangwagens en opleggers/Totaal aanhangwagens en opleggers (aantal)',
       'Wegvoertuigen per 1 januari/Bedrijfsvoertuigen/Aanhangwagens en opleggers/Aanhangwagen (aantal)',
       'Wegvoertuigen per 1 januari/Bedrijfsvoertuigen/Aanhangwagens en opleggers/Oplegger (aantal)']]
vrtg_verdeling.columns = vrtg_verdeling.columns.str.replace(r'Wegvoertuigen per 1 januari/Bedrijfsvoertuigen/', '')
vrtg_verdeling = vrtg_verdeling[["Regio's", "Bedrijfsmotorvoertuigen/Bestelauto (aantal)", 
                   "Bedrijfsmotorvoertuigen/Vrachtauto (excl. trekker voor oplegger) (aantal)", 
                  "Bedrijfsmotorvoertuigen/Trekker voor oplegger (aantal)"]]
vrtg_verdeling = vrtg_verdeling.rename(columns = {"Regio's" : "pc4", 
                                                  "Bedrijfsmotorvoertuigen/Bestelauto (aantal)": "pc4 Bestelwagen", 
                                                 "Bedrijfsmotorvoertuigen/Vrachtauto (excl. trekker voor oplegger) (aantal)":"pc4 Bakwagen", 
                                                 "Bedrijfsmotorvoertuigen/Trekker voor oplegger (aantal)":"pc4 Truck"})

anvu_vrtg = sndr[["Bedrijf", "Bedrijventerrein", "Kwaliteit data", 'pc4_y', 'Eigen wagenpark', 'Aantal truck',
       'Aantal bakwagen', 'Aantal bestelwagen', 'oppervlakte']]
anvu_vrtg = anvu_vrtg.rename(columns = {"pc4_y":"pc4"})

anvu_grp = anvu_vrtg.groupby("pc4").sum().reset_index()
vrtg_verdeling["pc4"] = vrtg_verdeling["pc4"].apply(str)

anvu_grp = anvu_grp.merge(vrtg_verdeling, on = "pc4")
anvu_grp = anvu_grp[["pc4", "pc4 Bestelwagen", "pc4 Bakwagen", "pc4 Truck", "oppervlakte"]]
anvu_grp = anvu_grp.rename(columns = {"oppervlakte":"pc4 Oppervlakte"})

stp_vrtg = anvu_vrtg[anvu_vrtg["Bedrijventerrein"] == "STP"]

stp_verd = vrtg_verdeling[vrtg_verdeling["pc4"] == "2133"]
stp_verd['pc4 Bestelwagen'] = stp_verd['pc4 Bestelwagen'] - stp_vrtg["Aantal bestelwagen"].sum()
stp_verd['pc4 Truck'] = stp_verd['pc4 Truck'] - stp_vrtg["Aantal truck"].sum()
stp_verd['pc4 Bakwagen'] = stp_verd['pc4 Bakwagen'] - stp_vrtg["Aantal bakwagen"].sum()
stp_verd = stp_verd.rename(columns = {"pc4 Bestelwagen":"Aantal bestelwagen", "pc4 Bakwagen":"Aantal bakwagen", 
                                     "pc4 Truck":"Aantal truck"})


stp_vrtg['Aantal truck'] = stp_vrtg['Aantal truck'].replace({np.nan: 0.0}).astype(int)
stp_vrtg['Aantal bakwagen'] = stp_vrtg['Aantal bakwagen'].replace({np.nan: 0.0}).astype(int)
stp_vrtg['Aantal bestelwagen'] = stp_vrtg['Aantal bestelwagen'].replace({np.nan: 0.0}).astype(int)

# Filter the DataFrame based on the "Kwaliteit data" column
df_brons = stp_vrtg[stp_vrtg['Kwaliteit data'] == 'Brons']

# Total number of vehicles to distribute
total_truck = int(stp_verd.iloc[0,3])
total_bakwagen = int(stp_verd.iloc[0,2])
total_bestelwagen = int(stp_verd.iloc[0,1])

# Distribute the vehicles randomly
for _ in range(total_truck):
    rand_index = random.choice(df_brons.index.to_list())
    df_brons.at[rand_index, 'Aantal truck'] += 1

for _ in range(total_bakwagen):
    rand_index = random.choice(df_brons.index.to_list())
    df_brons.at[rand_index, 'Aantal bakwagen'] += 1

for _ in range(total_bestelwagen):
    rand_index = random.choice(df_brons.index.to_list())
    df_brons.at[rand_index, 'Aantal bestelwagen'] += 1


# Merge the updated rows back into the original DataFrame
stp_vrtg.update(df_brons)

df = df.reset_index(drop = True)
df.update(stp_vrtg)

#Eigen voertuig afstand
sndr_afstand = df[['Bedrijf', 'Eigen wagenpark', 'Truck gem afstand in km', 'Bakwagen gem afstand in km',
       'Bestelwagen gem afstand in km', 'Truck max afstand in km',
       'Bakwagen max afstand in km', 'Bestelwagen max afstand in km']]
sndr_afstand = sndr_afstand.merge(verdeling, on = "Bedrijf")

sndr_afstand['Truck gem afstand in km'] = sndr_afstand['Truck gem afstand in km'].fillna(round(sndr_afstand['Truck gem afstand in km'].mean(),0))
sndr_afstand['Bakwagen gem afstand in km'] = sndr_afstand['Bakwagen gem afstand in km'].fillna(round(sndr_afstand['Bakwagen gem afstand in km'].mean(),0))
sndr_afstand['Bestelwagen gem afstand in km'] = sndr_afstand['Bestelwagen gem afstand in km'].fillna(round(sndr_afstand['Bestelwagen gem afstand in km'].mean(),0))
sndr_afstand['Truck max afstand in km'] = sndr_afstand['Truck max afstand in km'].fillna(round(sndr_afstand['Truck max afstand in km'].mean(),0))
sndr_afstand['Bakwagen max afstand in km'] = sndr_afstand['Bakwagen max afstand in km'].fillna(round(sndr_afstand['Bakwagen max afstand in km'].mean(),0))
sndr_afstand['Bestelwagen max afstand in km'] = sndr_afstand['Bestelwagen max afstand in km'].fillna(round(sndr_afstand['Bestelwagen max afstand in km'].mean(),0))

df.update(sndr_afstand)

#Parkeerplaatsen
sndr_park = df[['Bedrijf', 'Eigen wagenpark', 'Parkeerplaatsen']]
sndr_park = sndr_park.merge(verdeling, on = "Bedrijf")

park_mean = sndr_park[sndr_park["Parkeerplaatsen"].notna()]
park_mean["Parkeerplaatsen per m2 oppervlakte"] = park_mean["Parkeerplaatsen"]/park_mean["oppervlakte"]
sndr_park["Parkeerplaatsen per m2 oppervlakte"] = park_mean["Parkeerplaatsen per m2 oppervlakte"].mean()

sndr_park["Parkeerplaatsen"] = sndr_park["Parkeerplaatsen"].fillna(round(sndr_park["Parkeerplaatsen per m2 oppervlakte"]*sndr_park["oppervlakte"], 0))
df.update(sndr_park)

#Jaarverbruik
sndr_jaarverbruik = df[['Bedrijf', 'Eigen wagenpark', 'Jaarverbruik']]
sndr_jaarverbruik = sndr_jaarverbruik.merge(verdeling, on = "Bedrijf")

jaarverbruik_mean = sndr_jaarverbruik[sndr_jaarverbruik["Jaarverbruik"].notna()]
jaarverbruik_mean["Jaarverbruik per m2 oppervlakte"] = jaarverbruik_mean["Jaarverbruik"]/jaarverbruik_mean["oppervlakte"]
sndr_jaarverbruik["Jaarverbruik per m2 oppervlakte"] = jaarverbruik_mean["Jaarverbruik per m2 oppervlakte"].mean()

sndr_jaarverbruik["Jaarverbruik"] = sndr_jaarverbruik["Jaarverbruik"].fillna(round(sndr_jaarverbruik["Jaarverbruik per m2 oppervlakte"]*sndr_jaarverbruik["oppervlakte"], 0))

df["Jaarverbruik"] = sndr_jaarverbruik["Jaarverbruik"]


#Aansluiting pand
sndr_aansluiting = df[['Bedrijf', 'Eigen wagenpark', 'Vermogen aansluiting in watt (pand)']]
sndr_aansluiting = sndr_aansluiting.merge(verdeling, on = "Bedrijf")

aansluiting_mean = sndr_aansluiting[sndr_aansluiting["Vermogen aansluiting in watt (pand)"].notna()]
aansluiting_mean["Aansluiting per m2 oppervlakte"] = aansluiting_mean["Vermogen aansluiting in watt (pand)"]/aansluiting_mean["oppervlakte"]
sndr_aansluiting["Aansluiting per m2 oppervlakte"] = aansluiting_mean["Aansluiting per m2 oppervlakte"].mean()

sndr_aansluiting["Vermogen aansluiting in watt (pand)"] = sndr_aansluiting["Vermogen aansluiting in watt (pand)"].fillna(round(sndr_aansluiting["Aansluiting per m2 oppervlakte"]*sndr_aansluiting["oppervlakte"], 0))

df.update(sndr_aansluiting)

#ZEC Voorspelling
mask = df['Kwaliteit data'] == 'Brons'

# bakwagen vanf 2033 goedkoper -> 2035
# Copy values from "Aantal bakwagen" to "Voorspelling aantal elektrische bakwagen 2035"
df.loc[mask, 'Voorspelling aantal elektrische bakwagen 2035'] = df.loc[mask, 'Aantal bakwagen']
df.loc[mask, 'Voorspelling aantal elektrische bakwagen 2040'] = df.loc[mask, 'Aantal bakwagen']

# trucks vanaf 2032 goedkoper -> 2030
# Copy values from "Aantal truck" to "Voorspelling aantal elektrische truck 2030"
df.loc[mask, 'Voorspelling aantal elektrische truck 2030'] = df.loc[mask, 'Aantal truck']
df.loc[mask, 'Voorspelling aantal elektrische truck 2035'] = df.loc[mask, 'Aantal truck']
df.loc[mask, 'Voorspelling aantal elektrische truck 2040'] = df.loc[mask, 'Aantal truck']

# bestelwagen van 2040 goedkoper -> 2040
# Copy values from "Aantal bestelwagen" to "Voorspelling aantal elektrische bestelwagen 2040"
df.loc[mask, 'Voorspelling aantal elektrische bestelwagen 2040'] = df.loc[mask, 'Aantal bestelwagen']

#######################################
#######################################
#######################################

df.columns = df.columns.str.lower()
df = df[["bedrijf", "kwaliteit data", "aantal truck", "aantal bakwagen", "aantal bestelwagen", 'truck gem afstand in km', 
         'bakwagen gem afstand in km', 'bestelwagen gem afstand in km', 'truck max afstand in km', 'bakwagen max afstand in km', 'bestelwagen max afstand in km', "bezoekende truck per dag", 
         "bezoekende bakwagen per dag", "bezoekende bestelwagen per dag", "tijd bezoekend truck in minuten", "jaarverbruik", 
         "tijd bezoekend bakwagen in minuten", "tijd bezoekend bestelwagen in minuten", "vermogen aansluiting in watt (pand)",
         "voorspelling aantal elektrische bestelwagen 2025", "voorspelling aantal elektrische bakwagen 2025",
         "voorspelling aantal elektrische truck 2025", "voorspelling aantal elektrische bestelwagen 2030",
         "voorspelling aantal elektrische bakwagen 2030", "voorspelling aantal elektrische truck 2030",
         "voorspelling aantal elektrische bestelwagen 2035", "voorspelling aantal elektrische bakwagen 2035",
         "voorspelling aantal elektrische truck 2035", "voorspelling aantal elektrische bestelwagen 2040",
         "voorspelling aantal elektrische bakwagen 2040", "voorspelling aantal elektrische truck 2040"]]
df.columns = df.columns.str.replace(r'voorspelling aantal elektrische ', '')




# change company names
# Extract unique company names
unique_companies = df["bedrijf"].unique()

# Create a mapping from original company names to new anonymous names
company_mapping = {company: f"bedrijf {chr(i+65)}" for i, company in enumerate(unique_companies)}

# Replace the original company names with the new anonymous names
df["bedrijf"] = df["bedrijf"].replace(company_mapping)

def homepage():
         st.markdown(
                      """
                      <style>
                          .reportview-container .markdown-text-container {
                              text-align: center;
                          }
                      </style>
                      """,
                      unsafe_allow_html=True)
         st.markdown("<h1 style='text-align: center'>STP Bedrijventerrein</h1>", unsafe_allow_html=True)
         col1, col2 = st.columns(2)
         
         col1.write(""" \n\nDit dashboard geeft inzicht over het gebruik van elektriciteit op het bedrijventerrein Schiphol Trade Park. 
         Met de transitie naar elektrische voertuigen zal er meer gevraagd worden van het netwerk. 
         Door de ontwikkeling van de bedrijven en hun wagenpark in kaart te brengen kan er voorspeld worden hoe de stroomvraag zich ontwikkeld.
         
         \n\n Terwijl de wereld zich richt op duurzame energie, wordt de overstap naar elektrische voertuigen op bedrijventerreinen een groot en complex vraagstuk. 
         Het is algemeen bekend dat de elektriciteitsinfrastructuur in Nederland op sommige locaties al tegen zijn uiterste loopt.
         De transitie naar eleketrisch transport zal nog meer druk zetten op onze infrastructuur, zo ook op het bedrijventerrein Schiphol Trade Park.
         Dit betekent dat we geconfronteerd worden met een complexe puzzel die op de juiste manier moet worden aangepakt. 
         Dit dashboard biedt inzichten in de huidige situatie, uitdagingen en kansen binnen op het Schiphol Trade Park.\n\n""")
         

    



    # Render the map
         #col2.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=initial_view_state, map_style="mapbox://styles/mapbox/light-v9"))


    
    #### DATA
    # Load the geospatial data
         data = gpd.read_file("companies.gpkg")
         
         # Convert to EPSG:4326
         data = data.to_crs(epsg=4326)
         
         # Extract latitude and longitude for Pydeck
         data['lon'] = data['geometry'].x
         data['lat'] = data['geometry'].y

         # Create a Pydeck map
         map = pdk.Deck(
             map_style="mapbox://styles/mapbox/light-v9",
             initial_view_state={
                 "latitude": data['lat'].mean(),
                 "longitude": data['lon'].mean(),
                 "zoom": 13,
             },
             layers=[
                 pdk.Layer(
                     "ScatterplotLayer",
                     data,
                     get_position=["lon", "lat"],
                     get_radius=100,
                     get_fill_color=[255, 0, 0, 140],
                     pickable=True,
                     auto_highlight=True,
                     
                 ),
             ],
                  tooltip={"text": "Bedrijf: {Bedrijf}"}
         )
         
         col2.pydeck_chart(map)


         # Insights

         cols = st.columns(4)
         
         icon_bakwagen = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bakwagen.jpg"
         aantal_bakwagen = int(df["aantal bakwagen"].sum())
         icon_bakwagen_html = f'''<img src="{icon_bakwagen}" width="150" style="display: block; margin: auto;">'
         <p style="text-align: center; font-size: 24px;">{aantal_bakwagen} Bakwagens</p>'''
         
         icon_bestelwagen = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bestelwagen.jpg"
         aantal_bestelwagen = int(df["aantal bestelwagen"].sum())
         icon_bestelwagen_html = f'''<img src="{icon_bestelwagen}" width="150" style="display: block; margin: auto;">'
         <p style="text-align: center; font-size: 24px;">{aantal_bestelwagen} Bestelwagens</p>'''
         
         icon_truck = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20truck.jpg"
         aantal_truck = int(df["aantal truck"].sum())
         icon_truck_html = f'''<img src="{icon_truck}" width="150" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 24px;">{aantal_truck} Trucks</p>'''
         
         icon_bedrijf = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bedrijf.jpg"
         aantal_bedrijf = len(df['bedrijf'].unique())
         icon_bedrijf_html = f'''<img src="{icon_bedrijf}" width="150" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 24px;">{aantal_bedrijf} Bedrijven</p>'''
         
         
         
         # Display content in the first column
         #cols[0].markdown(icon_bedrijf, caption="Bedrijf Icon", use_column_width=False, width=150)
         cols[0].markdown(icon_bedrijf_html, unsafe_allow_html=True)
         cols[1].markdown(icon_truck_html, unsafe_allow_html=True)
         cols[2].markdown(icon_bestelwagen_html, unsafe_allow_html=True)
         cols[3].markdown(icon_bakwagen_html, unsafe_allow_html=True)


                  
         
         
 
         
         


def bsg_page():
         st.markdown(
                      """
                      <style>
                          .reportview-container .markdown-text-container {
                              text-align: center;
                          }
                      </style>
                      """,
                      unsafe_allow_html=True)
         st.markdown("<h1 style='text-align: center'>Brons, Zilver of Goud</h1>", unsafe_allow_html=True)

         
         text1, text2, text3 = st.columns([0.45,0.1,0.45])

         text1.write(""" \n\n\n\nOm inzicht te geven in de toekomstige energiegebruik van het bedrijventerrein is het van belang om te weten 
         hoe de huidige situatie eruit ziet. Aan de hand van data en enquetes kan er achterhaald worden hoe het het huidige energieverbuik eruit ziet en wat voor
         invloed de overstap naar elektrische voertuigen zal hebben. Het type en aantal voertuigen per bedrijf kan laten zien hoe de toekomstige situatie van 
         het wagenpark eruit ziet. \n\nLang niet alle bedrijven hebben echter de tijd of mogelijkheid om deze data te leveren. 
         In dit geval moet er a.d.h.v openbare data schattingen 
         gemaakt worden. Deze data en de data van de participerende bedrijven vormen samen de informatie over het gehele bedrijventerrein. 
         Alleen zo kunnen er inzichten worden gegeven over het gehele bedrijventerrein. 
         \n\nOm de gaten op te vullen is er gebruik gemaakt van data van het CBS en PDOK. De data van de CBS geeft per PC4 gebied aan hoeveel type 
         voertuigen er zich in het gebied bevinden. De PDOK data geeft informatie over de grootte van de panden van de bedrijven. 
         \n\nOm de kwaliteit van de data aan te geven wordt er in het dashboard gebruik gemaakt van een "Brons-Zilver-Goud Systeem". Dit systeem geeft aan waar 
         de data vandaan komt en hoe deze gebruikt is. De tabel recht geeft dit weer.
         \n\n\n\n""")


         table_html = """
             <style>
                 table {
                     font-size: 20px; /* Adjust as necessary */
                     width: 100%;
                 }
                 td, th {
                     padding: 15px; /* Adjust as necessary */
                     text-align: center;
                 }
                 .gold { color: gold; }
                 .silver { color: silver; }
                 .bronze { color: #cd7f32; }  <!-- Bronze color -->
                 .green-check { color: green; }
                 .red-cross { color: red; }
             </style>
             <table>
                 <tr>
                     <th>Data type</th>
                     <th class="gold">Goud</th>
                     <th class="silver">Zilver</th>
                     <th class="bronze">Brons</th>
                 </tr>
                 <tr>
                     <td>Ritten data</td>
                     <td class="green-check">✓</td>
                     <td class="red-cross">✗</td>
                     <td class="red-cross">✗</td>
                 </tr>
                 <tr>
                     <td>Enquete data</td>
                     <td class="green-check">✓</td>
                     <td class="green-check">✓</td>
                     <td class="red-cross">✗</td>
                 </tr>
                 <tr>
                     <td>Openbare data</td>
                     <td class="green-check">✓</td>
                     <td class="green-check">✓</td>
                     <td class="green-check">✓</td>
                 </tr>
             </table>
             """

         text3.write("Data type Tabel")
         text3.markdown(table_html, unsafe_allow_html=True)

         
         
         column0, column1, column2, column3, column4, column5 = st.columns([0.2,0.2,0.2,0.2,0.1,0.3])


         #Bedrijven
         icon_bedrijf = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bedrijf.jpg"
         aantal_bedrijf = len(df['bedrijf'].unique())
         icon_bedrijf_html = f'''<img src="{icon_bedrijf}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bedrijf} Bedrijven</p>'''    
         column0.markdown(icon_bedrijf_html, unsafe_allow_html=True)
         column0.write("--------------------------------------------------------------------------------------------------------------------------")

         icon_bedrijf_goud = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bedrijf%20goud.jpg"
         aantal_bedrijf_goud = len(df[df["kwaliteit data"] == "Goud"]["bedrijf"])
         icon_bedrijf_goud_html = f'''<img src="{icon_bedrijf_goud}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bedrijf_goud} Bedrijven</p>'''    
         column0.markdown(icon_bedrijf_goud_html, unsafe_allow_html=True)

         icon_bedrijf_zilver = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bedrijf%20zilver.jpg"
         aantal_bedrijf_zilver = len(df[df["kwaliteit data"] == "Zilver"]["bedrijf"])
         icon_bedrijf_zilver_html = f'''<img src="{icon_bedrijf_zilver}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bedrijf_zilver} Bedrijven</p>'''    
         column0.markdown(icon_bedrijf_zilver_html, unsafe_allow_html=True)

         icon_bedrijf_brons = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bedrijf%20brons.jpg"
         aantal_bedrijf_brons = len(df[df["kwaliteit data"] == "Brons"]["bedrijf"])
         icon_bedrijf_brons_html = f'''<img src="{icon_bedrijf_brons}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bedrijf_brons} Bedrijven</p>'''    
         column0.markdown(icon_bedrijf_brons_html, unsafe_allow_html=True)
         
         

         #TRUCK
         icon_truck = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20truck.jpg"
         aantal_truck = int(df["aantal truck"].sum())
         icon_truck_html = f'''<img src="{icon_truck}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_truck} Truck</p>'''
         column1.markdown(icon_truck_html, unsafe_allow_html=True)
         column1.write("--------------------------------------------------------------------------------------------------------------------------")

         icon_truck_goud = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20truck%20goud.jpg"
         aantal_truck_goud = int(df[df["kwaliteit data"] == "Goud"]["aantal truck"].sum())
         icon_truck_goud_html = f'''<img src="{icon_truck_goud}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_truck_goud} Truck</p>'''
         column1.markdown(icon_truck_goud_html, unsafe_allow_html=True)
         
         icon_truck_zilver = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20truck%20zilver.jpg"
         aantal_truck_zilver = int(df[df["kwaliteit data"] == "Zilver"]["aantal truck"].sum())
         icon_truck_zilver_html = f'''<img src="{icon_truck_zilver}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_truck_zilver} Truck</p>'''
         column1.markdown(icon_truck_zilver_html, unsafe_allow_html=True)

         icon_truck_brons = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20truck%20brons.jpg"
         aantal_truck_brons = int(df[df["kwaliteit data"] == "Brons"]["aantal truck"].sum())
         icon_truck_brons_html = f'''<img src="{icon_truck_brons}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_truck_brons} Truck</p>'''
         column1.markdown(icon_truck_brons_html, unsafe_allow_html=True)

         #BAKWAGEN
         icon_bakwagen = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bakwagen.jpg"
         aantal_bakwagen = int(df["aantal bakwagen"].sum())
         icon_bakwagen_html = f'''<img src="{icon_bakwagen}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bakwagen} Bakwagens</p>'''
         column2.markdown(icon_bakwagen_html, unsafe_allow_html=True)
         column2.write("--------------------------------------------------------------------------------------------------------------------------")

         icon_bakwagen_goud = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bakwagen%20goud.jpg"
         aantal_bakwagen_goud = int(df[df["kwaliteit data"] == "Goud"]["aantal bakwagen"].sum())
         icon_bakwagen_goud_html = f'''<img src="{icon_bakwagen_goud}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bakwagen_goud} Bakwagens</p>'''
         column2.markdown(icon_bakwagen_goud_html, unsafe_allow_html=True)
         
         icon_bakwagen_zilver = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bakwagen%20zilver.jpg"
         aantal_bakwagen_zilver = int(df[df["kwaliteit data"] == "Zilver"]["aantal bakwagen"].sum())
         icon_bakwagen_zilver_html = f'''<img src="{icon_bakwagen_zilver}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bakwagen_zilver} Bakwagens</p>'''
         column2.markdown(icon_bakwagen_zilver_html, unsafe_allow_html=True)

         icon_bakwagen_brons = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bakwagen%20brons.jpg"
         aantal_bakwagen_brons = int(df[df["kwaliteit data"] == "Brons"]["aantal bakwagen"].sum())
         icon_bakwagen_brons_html = f'''<img src="{icon_bakwagen_brons}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bakwagen_brons} bakwagen</p>'''
         column2.markdown(icon_bakwagen_brons_html, unsafe_allow_html=True)


         #BESTELWAGEN
         icon_bestelwagen = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bestelwagen.jpg"
         aantal_bestelwagen = int(df["aantal bestelwagen"].sum())
         icon_bestelwagen_html = f'''<img src="{icon_bestelwagen}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bestelwagen} bestelwagen</p>'''
         column3.markdown(icon_bestelwagen_html, unsafe_allow_html=True)
         column3.write("--------------------------------------------------------------------------------------------------------------------------")

         icon_bestelwagen_goud = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bestelwagen%20goud.jpg"
         aantal_bestelwagen_goud = int(df[df["kwaliteit data"] == "Goud"]["aantal bestelwagen"].sum())
         icon_bestelwagen_goud_html = f'''<img src="{icon_bestelwagen_goud}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bestelwagen_goud} bestelwagen</p>'''
         column3.markdown(icon_bestelwagen_goud_html, unsafe_allow_html=True)
         
         icon_bestelwagen_zilver = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bestelwagen%20zilver.jpg"
         aantal_bestelwagen_zilver = int(df[df["kwaliteit data"] == "Zilver"]["aantal bestelwagen"].sum())
         icon_bestelwagen_zilver_html = f'''<img src="{icon_bestelwagen_zilver}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bestelwagen_zilver} bestelwagen</p>'''
         column3.markdown(icon_bestelwagen_zilver_html, unsafe_allow_html=True)

         icon_bestelwagen_brons = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bestelwagen%20brons.jpg"
         aantal_bestelwagen_brons = int(df[df["kwaliteit data"] == "Brons"]["aantal bestelwagen"].sum())
         icon_bestelwagen_brons_html = f'''<img src="{icon_bestelwagen_brons}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bestelwagen_brons} bestelwagen</p>'''
         column3.markdown(icon_bestelwagen_brons_html, unsafe_allow_html=True)

         


         # Create a dataframe
         df_voertuigen = df[['kwaliteit data', 'aantal truck', 'aantal bakwagen', 'aantal bestelwagen']]
         df_voertuigen = df_voertuigen.groupby(by = "kwaliteit data").sum()
         df_voertuigen["aantal"] = df_voertuigen['aantal truck'] + df_voertuigen['aantal bakwagen'] + df_voertuigen['aantal bestelwagen']
         df_voertuigen = df_voertuigen.reindex(['Goud', 'Zilver', 'Brons'])
         
         labels = df_voertuigen.index.tolist()
         colors = ['gold', 'silver', '#cd7f32']  # gold, silver, bronze colors
         explode = (0.5, 0.25, 0)  # explode only the gold slice
         fig5, ax5 = plt.subplots(figsize=(2.5, 2.5))
         ax5.pie(df_voertuigen['aantal'], explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
         column5.write('De onderstaande grafiek geeft weer dat een groot deel van het aantal voertuigen bestaat uit de geschatte data')
         column5.pyplot(fig5)
         
                  

         # UITLEG SCHATTINGEN

         uitleg0, uitleg1, uitleg2 = st.columns([0.4,0.2,0.4])

         uitleg0.title("Voertuigen")
         uitleg0.write("""Om het aantal voertuigen per bedrijf te bepalen wordt er eerst gekeken naar de enquetedata. Hierin hebben bedrijven ingevuld hoeveel 
         voertuigen zij hebben. Echter hebben niet alle bedrijven dat gedaan. Om een compleet beeld te geven van het wagenpark van het bedrijventerrein wordt er
         gekeken naar cbs data: https://opendata.cbs.nl/#/CBS/nl/dataset/37209hvv/table . \n\nDe voertuigen die in de enquetes naar boven kwamen worden van 
         de voertuigen van cbs afgetrokken. De resterende voertuigen worden vervolgens verdeeld over de "bronze" bedrijven. Deze verdeling is willekeurig.""")
         df_anv_voertuigen = df[["bedrijf", "kwaliteit data", "aantal truck", "aantal bakwagen", "aantal bestelwagen"]]
         
         st.markdown("""
         <style>
                 .stTable {
                     height: 300px;  /* Adjust height as necessary */
                     overflow-y: auto;
                     display: block;
                 }
         </style>
         """, unsafe_allow_html=True)

         uitleg0.write(df_anv_voertuigen)

         uitleg2.title("Gereden kilometers")
         uitleg2.write("""Om de impact van de voertuigen op het netwerk te weten, moeten wij eerst weten hoeveel kilometer zij rijden. Het aantal gereden 
         kilometers kan vervolgens worden omgerekend naar een hoeveelheid kWh wat geladen moet worden. De bedrijven die de enquete hebben ingevuld hebben 
         aangegeven hoeveel kilometer zij gemiddeld en maximaal op een dag rijden, i.c.m. het aantal voertuigen kan er een beeld geschetst worden van de 
         toekomstige laadvraag. We beschikken niet over het aantal gereden kilometers van de "bronze" bedrijven. Om dit te bepalen is er gekeken naar de 
         hoeveelheid gereden kilometers van de zilvere en gouden bedrijven. Hiervan is een gemiddelde genomen per voertuig, deze is vervolgens toegewezen 
         aan de bronze voertuigen""")
         df_anv_afstand = df[["bedrijf", "kwaliteit data", 'truck gem afstand in km', 'bakwagen gem afstand in km',
                                                 'bestelwagen gem afstand in km', 'truck max afstand in km', 'bakwagen max afstand in km', 
                                                 'bestelwagen max afstand in km']]

         st.markdown("""
         <style>
                 .stTable {
                     height: 300px;  /* Adjust height as necessary */
                     overflow-y: auto;
                     display: block;
                 }
         </style>
         """, unsafe_allow_html=True)

         uitleg2.write(df_anv_afstand)
         


         uitleg0.title("Jaarverbruik pand")
         uitleg0.write("""uitleg over bepalen jaarverbruik pand 
         \n\n is bepaald adhv gemiddelde zilver en goud, ...kwh per m2""")
         df_anv_verbruik = df[["bedrijf", "kwaliteit data", "jaarverbruik"]]
         
         st.markdown("""
         <style>
                 .stTable {
                     height: 300px;  /* Adjust height as necessary */
                     overflow-y: auto;
                     display: block;
                 }
         </style>
         """, unsafe_allow_html=True)

         uitleg0.write(df_anv_verbruik)

         uitleg2.title("Aansluiting pand")
         uitleg2.write("""uitleg over aansluiting pand
         \n\n\n\n is bepaald adhv gemiddelde zilver en goud, ...kwh per m2""")
         df_anv_aansluiting = df[["bedrijf", "kwaliteit data", "vermogen aansluiting in watt (pand)"]]
         
         st.markdown("""
         <style>
                 .stTable {
                     height: 300px;  /* Adjust height as necessary */
                     overflow-y: auto;
                     display: block;
                 }
         </style>
         """, unsafe_allow_html=True)

         uitleg2.write(df_anv_aansluiting)
         
         uitleg0.title("Voorspelling Wagenpark")
         uitleg0.write("uitleg over bepalen overstap naar elektrisch \n\nIs bepaald adhv aanschafprijs EV goedkoper dan diesel. truck -> 2030, bakwagen -> 2035, bestelwagen -> 2040")
         df2 = df
         


    

    
def vehicle_page(): 
                  
         st.markdown(
                      """
                      <style>
                          .reportview-container .markdown-text-container {
                              text-align: center;
                          }
                      </style>
                      """,
                      unsafe_allow_html=True)
         st.markdown("<h1 style='text-align: center'>Voertuigen en pand</h1>", unsafe_allow_html=True)

         
         # add columns
         col1, col2 = st.columns(2)

         # Place text in the left column
         col1.write(""" Dit dashboard geeft inzicht over het gebruik van elektriciteit op het bedrijventerrein Schiphol Trade Park. 
         Met de transitie naar elektrische voertuigen zal er meer gevraagd worden van het netwerk. 
         Door de ontwikkeling van de bedrijven en hun wagenpark in kaart te brengen kan er voorspeld worden hoe de stroomvraag zich ontwikkeld.
         
         \n\n Terwijl de wereld zich richt op duurzame energie, wordt de overstap naar elektrische voertuigen op bedrijventerreinen een groot en complex vraagstuk. 
         Het is algemeen bekend dat de elektriciteitsinfrastructuur in Nederland op sommige locaties al tegen zijn uiterste loopt.
         De transitie naar eleketrisch transport zal nog meer druk zetten op onze infrastructuur, zo ook op het bedrijventerrein Schiphol Trade Park.
         Dit betekent dat we geconfronteerd worden met een complexe puzzel die op de juiste manier moet worden aangepakt. 
         Dit dashboard biedt inzichten in de huidige situatie, uitdagingen en kansen binnen op het Schiphol Trade Park.""")  # Replace with your desired text

         # capacity line
         show_line = col1.checkbox('Capaciteit netwerk')


         
         # The user can select a year
         year = col1.selectbox('Select a year', options=[2025, 2030, 2035, 2040])
         
         # The user can select between maximum and average
         value_type = col1.radio('Choose a value type', options=['max', 'gem'])

         adjustment_value = col1.number_input('upgrade netwerk', value=0.0)

         df


       
       
       
       
       
         

def company_page():
         st.title('Bedrijven')
         # Title
         st.markdown(
                      """
                      <style>
                          .reportview-container .markdown-text-container {
                              text-align: center;
                          }
                      </style>
                      """,
                      unsafe_allow_html=True)
         st.markdown("<h1 style='text-align: center'>Bedrijven</h1>", unsafe_allow_html=True)

         # add columns
         col1, col2 = st.columns(2)

         df
         
         # Place text in the left column
         col1.text("Tekst over gebruik bedrijven")  # Replace with your desired text

         # capacity line
         show_line = col1.checkbox('Capaciteit netwerk')
         
         # The user can select a year
         year = col1.selectbox('Select a year', options=[2025, 2030, 2035, 2040])
         
         # The user can select between maximum and average
         value_type = col1.radio('Choose a value type', options=['max', 'gem'])

         adjustment_value = col1.number_input('upgrade netwerk', value=0.0)
         
         if value_type:
                  usage_column = f'max verbruik in kWh {year}'
         else:
                  usage_column = f'gem verbruik in kWh {year}'


         
         toename_df = df[df["Datum"] == "2022-10-3 17:00:00"]
         toename_df = toename_df[['bedrijf', 'Verbruik pand in kWh', 'max verbruik in kWh 2025', 'max verbruik in kWh 2030', 'max verbruik in kWh 2035', 'max verbruik in kWh 2040']] 
         toename_df = toename_df.rename(columns={'Verbruik pand in kWh':'Max verbruik in kWh 2023'})
         toename_df.columns = toename_df.columns.str.replace(r'max verbruik ', '')
         toename_df.columns = toename_df.columns.str.replace(r'in kWh ', '')
         toename_df = toename_df.set_index("bedrijf").transpose()
         
         
         # Plotting
         fig5, ax5 = plt.subplots(figsize=(6,3))
         toename_df.plot(kind='area', stacked=True, title=f'Toename piek stroomnet', ax=ax5)
         ax5.axhline(y=8000 + adjustment_value, color='black', linestyle='--')
         # Adjusting title font size
         #ax5.set_title(f'Toename piek stroomnet', fontsize=6)
         
         # Adjusting axis label font sizes
         #ax5.set_xlabel('Year', fontsize=6)
         #ax5.set_ylabel('Value', fontsize=6)
         
         # Adjusting tick font sizes
         #ax5.tick_params(axis='both', which='major', labelsize=6)
         
         # Adjusting legend font size
         #ax5.legend(fontsize=8)
         col2.pyplot(fig5, use_container_width=True)
         
         

         
         #### Year
         df_yearly_company = df.groupby(['Year', 'Month', 'bedrijf'])[usage_column].sum().unstack()
         
         #### MONTH
         # Group by year, month and calculate the sum of 'Max verbruik in kWh 2040' for all companies
         df_monthly_total_company = df.groupby(['Year', 'Month'])[usage_column].sum()
         
         # Find the month with the highest total usage
         highest_month_company = df_monthly_total_company.idxmax()
         
         # Select data for the highest usage month
         df_highest_month_company = df[(df['Year'] == highest_month_company[0]) & (df['Month'] == highest_month_company[1])]
         
         # Group by day and 'Bedrijf', and calculate the sum of 'Max verbruik in kWh 2040'
         df_monthly_highest_company = df_highest_month_company.groupby(['Day', 'Bedrijf'])[usage_column].sum().unstack()
         
         
         #### WEEK
         # Group by year, week and calculate the sum of 'Max verbruik in kWh 2040' for all companies
         df_weekly_total_company = df.groupby(['Year', 'Week'])[usage_column].sum()
         
         # Find the week with the highest total usage
         highest_week_company = df_weekly_total_company.idxmax()
         
         # Select data for the highest usage week
         df_highest_week_company = df[(df['Year'] == highest_week_company[0]) & (df['Week'] == highest_week_company[1])]
         
         # Group by weekday and 'Bedrijf', and calculate the sum of 'Max verbruik in kWh 2040'
         df_weekly_highest_company = df_highest_week_company.groupby(['Weekday', 'Bedrijf'])[usage_column].sum().unstack()
                  
         
         
         #### DAY
        # Group by year, month, day and calculate the sum of 'Max verbruik in kWh 2040' for all companies
         df_daily_total_company = df.groupby(['Year', 'Month', 'Day'])[usage_column].sum()
         
         # Find the day with the highest total usage
         highest_day_company = df_daily_total_company.idxmax()
         
         # Select data for the highest usage day
         df_highest_day_company = df[(df['Year'] == highest_day_company[0]) & (df['Month'] == highest_day_company[1]) & (df['Day'] == highest_day_company[2])]
         
         # Group by hour and 'Bedrijf', and calculate the sum of 'Max verbruik in kWh 2040'
         df_daily_highest_company = df_highest_day_company.groupby(['Hour', 'Bedrijf'])[usage_column].sum().unstack()
         
         
         
         #### PLOT
         # Create a 1x4 layout
         cols = st.columns(4)
         
         
         # Create the first chart
         fig1, ax1 = plt.subplots()
         df_yearly_company.plot(kind='area', stacked=True, title='Yearly Electricity Usage per Company', ax=ax1)
         ax1.set_ylim([0, df.groupby(['Year', 'Month'])["max verbruik in kWh 2040"].sum().max()])
         ax1.legend().set_visible(False)
         # cols[0].pyplot(fig1)
         
         
         # Create the second chart
         fig2, ax2 = plt.subplots()
         df_monthly_highest_company.plot(kind='area', stacked=True, 
                            title=f'Monthly Electricity Usage per Company (Highest Usage Month: {highest_month_company[0]}-{highest_month_company[1]})', ax=ax2)
         ax2.set_ylim([0, df_highest_week_company.groupby('Weekday')["max verbruik in kWh 2040"].sum().max()])
         ax2.legend().set_visible(False)
         
         # cols[1].pyplot(fig2)
         
         # Create the third chart
         fig3, ax3 = plt.subplots()
         df_weekly_highest_company.plot(kind='area', stacked=True, 
                           title=f'Weekly Electricity Usage per Company (Highest Usage Week: {highest_week_company[0]}-Week {highest_week_company[1]})', ax=ax3)
         ax3.set_ylim([0, df_highest_week_company.groupby('Weekday')["max verbruik in kWh 2040"].sum().max()])
         ax3.legend().set_visible(False)

         
         # Create the fourth chart
         fig4, ax4 = plt.subplots()
         df_daily_highest_company.plot(kind='area', stacked=True, 
                          title=f'Daily Electricity Usage per Company (Highest Usage Day: {highest_day_company[0]}-{highest_day_company[1]}-{highest_day_company[2]})', ax=ax4)
         ax4.set_ylim([0, df_highest_day_company.groupby('Hour')["max verbruik in kWh 2040"].sum().max()])
         ax4.legend().set_visible(False)


         if show_line:
                  ax1.axhline(y=1500000 + adjustment_value, color='black', linestyle='--')
                  ax2.axhline(y=50000 + adjustment_value, color='black', linestyle='--')
                  ax3.axhline(y=40000 + adjustment_value, color='black', linestyle='--')
                  ax4.axhline(y=7500 + adjustment_value, color='black', linestyle='--')

         # Display the plots
         cols[0].pyplot(fig1)
         cols[1].pyplot(fig2)
         cols[2].pyplot(fig3)
         cols[3].pyplot(fig4)
    
       
       
       
       
         

def ffkijken():
         # Title
         st.markdown(
                      """
                      <style>
                          .reportview-container .markdown-text-container {
                              text-align: center;
                          }
                      </style>
                      """,
                      unsafe_allow_html=True)
         st.markdown("<h1 style='text-align: center'>Voertuigen en pand</h1>", unsafe_allow_html=True)

         # add columns
         col1, col2 = st.columns(2)

         # Place text in the left column
         col1.text(""" aaDit dashboard geeft inzicht over het gebruik van elektriciteit op het bedrijventerrein Schiphol Trade Park. 
         Met de transitie naar elektrische voertuigen zal er meer gevraagd worden van het netwerk. 
         Door de ontwikkeling van de bedrijven en hun wagenpark in kaart te brengen kan er voorspeld worden hoe de stroomvraag zich ontwikkeld.
         
         \n\n Terwijl de wereld zich richt op duurzame energie, wordt de overstap naar elektrische voertuigen op bedrijventerreinen een groot en complex vraagstuk. 
         Het is algemeen bekend dat de elektriciteitsinfrastructuur in Nederland op sommige locaties al tegen zijn uiterste loopt.
         De transitie naar eleketrisch transport zal nog meer druk zetten op onze infrastructuur, zo ook op het bedrijventerrein Schiphol Trade Park.
         Dit betekent dat we geconfronteerd worden met een complexe puzzel die op de juiste manier moet worden aangepakt. 
         Dit dashboard biedt inzichten in de huidige situatie, uitdagingen en kansen binnen op het Schiphol Trade Park.""")  # Replace with your desired text

         # capacity line
         show_line = col1.checkbox('Capaciteit netwerk')
         
         # The user can select a year
         year = col1.selectbox('Select a year', options=[2025, 2030, 2035, 2040])
         
         # The user can select between maximum and average
         value_type = col1.radio('Choose a value type', options=['max', 'gem'])

         adjustment_value = col1.number_input('upgrade netwerk', value=0.0)
         



         
         toename_df = df[df["Datum"] == "2022-10-3 17:00:00"]
         toename_df = toename_df[['truck max verbruik 2025 in kWh', 'bakwagen max verbruik 2025 in kWh',
                'bestelwagen max verbruik 2025 in kWh', 'voertuigen max verbruik 2025 in kWh', 'truck max verbruik 2030 in kWh',
                'bakwagen max verbruik 2030 in kWh', 'bestelwagen max verbruik 2030 in kWh', 'voertuigen max verbruik 2030 in kWh', 
                'truck max verbruik 2035 in kWh', 'bakwagen max verbruik 2035 in kWh', 'bestelwagen max verbruik 2035 in kWh',
                'voertuigen max verbruik 2035 in kWh', 'truck max verbruik 2040 in kWh', 'bakwagen max verbruik 2040 in kWh',
                'bestelwagen max verbruik 2040 in kWh', 'voertuigen max verbruik 2040 in kWh']] 
         toename_df.columns = toename_df.columns.str.replace(r'max verbruik ', '')
         toename_df.columns = toename_df.columns.str.replace(r' in kWh', '')
         toename_df = pd.DataFrame(toename_df.sum()).reset_index().rename(columns = {"index":"type_year", 0:"value"})
         
         # Split the 'type_year' column into 'type' and 'year'
         toename_df[['type', 'year']] = toename_df['type_year'].str.split(' ', expand=True)
         
         # Pivot the DataFrame to the desired shape
         toename_df = toename_df.pivot(index='year', columns='type', values='value').reset_index()
         toename_df["pand"] = df[df["Datum"] == "2022-10-3 17:00:00"]['Verbruik pand in kWh'].sum()
         toename_df.loc[4] = [2023,0,0,0,0,4257.813287]
         toename_df['year'] = toename_df['year'].astype(int)
         toename_df = toename_df.sort_values(by = 'year')
         toename_df = toename_df.set_index('year')[['pand','truck','bakwagen', 'bestelwagen', 'voertuigen']]

         option = col2.radio('Weergave plot', ['Wagenpark', 'Per voertuig'])
         
         if option == 'Wagenpark':
             columns_to_display = ['pand', 'voertuigen']
         else:
             columns_to_display = ['pand', 'truck', 'bakwagen', 'bestelwagen']
         
         # Plotting
         fig5, ax5 = plt.subplots(figsize=(6,3))
         toename_df[columns_to_display].plot(kind='area', stacked=True, title=f'Toename piek stroomnet', ax=ax5)
         ax5.axhline(y=8000 + adjustment_value, color='black', linestyle='--')
         # Adjusting title font size
         ax5.set_title(f'Toename piek stroomnet', fontsize=6)
         
         # Adjusting axis label font sizes
         ax5.set_xlabel('Year', fontsize=6)
         ax5.set_ylabel('Value', fontsize=6)
         
         # Adjusting tick font sizes
         ax5.tick_params(axis='both', which='major', labelsize=6)
         
         # Adjusting legend font size
         ax5.legend(fontsize=8)
         col2.pyplot(fig5, use_container_width=True)
         
         
         # Based on the user's selections, choose the appropriate columns
         truck_usage_column = f'truck {value_type} verbruik {year} in kWh'
         bakwagen_usage_column = f'bakwagen {value_type} verbruik {year} in kWh'
         bestelwagen_usage_column = f'bestelwagen {value_type} verbruik {year} in kWh'
         pand_usage_column = 'Verbruik pand in kWh'
         
         #### Year
         df_yearly_vehicle = df.groupby(['Year', 'Month'])[[truck_usage_column, bakwagen_usage_column, bestelwagen_usage_column, pand_usage_column]].sum()
         
         #### MONTH
         # Group by year, month and calculate the sum of all vehicle types
         df_monthly_total_vehicle = df.groupby(['Year', 'Month'])[[truck_usage_column, bakwagen_usage_column, bestelwagen_usage_column, pand_usage_column]].sum()
         df_monthly_total_vehicle['Total'] = df_monthly_total_vehicle.sum(axis=1)
         
         # Find the month with the highest total usage
         highest_month_vehicle = df_monthly_total_vehicle[df_monthly_total_vehicle['Total'] == df_monthly_total_vehicle['Total'].max()]
         highest_year_month_vehicle = highest_month_vehicle[['Total']].idxmax()[0]
         
         # Select data for the highest usage month
         df_highest_month_vehicle = df[(df['Year'] == highest_year_month_vehicle[0]) & (df['Month'] == highest_year_month_vehicle[1])]
         
         # Group by day and calculate the sum of the specified columns
         df_monthly_highest_vehicle = df_highest_month_vehicle.groupby(['Day'])[[truck_usage_column, bakwagen_usage_column, bestelwagen_usage_column, pand_usage_column]].sum()
         
         
         #### WEEK
         # Group by year, week and calculate the sum of all vehicle types
         df_weekly_total_vehicle = df.groupby(['Year', 'Week'])[[truck_usage_column, bakwagen_usage_column, bestelwagen_usage_column, pand_usage_column]].sum()
         df_weekly_total_vehicle['Total'] = df_weekly_total_vehicle.sum(axis=1)
         
         # Find the week with the highest total usage
         highest_week_vehicle = df_weekly_total_vehicle[df_weekly_total_vehicle['Total'] == df_weekly_total_vehicle['Total'].max()]
         highest_year_week_vehicle = highest_week_vehicle[['Total']].idxmax()[0]
         
         # Select data for the highest usage week
         df_highest_week_vehicle = df[(df['Year'] == highest_year_week_vehicle[0]) & (df['Week'] == highest_year_week_vehicle[1])]
         
         # Group by weekday and calculate the sum of the specified columns
         df_weekly_highest_vehicle = df_highest_week_vehicle.groupby(['Weekday'])[[truck_usage_column, bakwagen_usage_column, bestelwagen_usage_column, pand_usage_column]].sum()
         
         
         
         #### DAY
         # Group by year, month, day and calculate the sum of all vehicle types
         df_daily_total_vehicle = df.groupby(['Year', 'Month', 'Day'])[[truck_usage_column, bakwagen_usage_column, bestelwagen_usage_column, pand_usage_column]].sum()
         df_daily_total_vehicle['Total'] = df_daily_total_vehicle.sum(axis=1)
         
         # Find the day with the highest total usage
         highest_day_vehicle = df_daily_total_vehicle[df_daily_total_vehicle['Total'] == df_daily_total_vehicle['Total'].max()]
         highest_year_month_day_vehicle = highest_day_vehicle[['Total']].idxmax()[0]
         
         # Select data for the highest usage day
         df_highest_day_vehicle = df[(df['Year'] == highest_year_month_day_vehicle[0]) & (df['Month'] == highest_year_month_day_vehicle[1]) & (df['Day'] == highest_year_month_day_vehicle[2])]
         
         # Group by hour and calculate the sum of the specified columns
         df_daily_highest_vehicle = df_highest_day_vehicle.groupby(['Hour'])[[truck_usage_column, bakwagen_usage_column, bestelwagen_usage_column, pand_usage_column]].sum()
         
         
         
         #### PLOT
         # Create a 1x4 layout
         cols = st.columns(4)
         
         
         # Create the first chart
         fig1, ax1 = plt.subplots()
         df_yearly_vehicle.plot(kind='area', stacked=True, title='Yearly Electricity Usage', ax=ax1)
         ax1.set_ylim([0, df.groupby(['Year', 'Month'])["max verbruik in kWh 2040"].sum().max()])
         # cols[0].pyplot(fig1)
         
         
         # Create the second chart
         fig2, ax2 = plt.subplots()
         df_monthly_highest_vehicle.plot(kind='area', stacked=True, 
                            title=f'Monthly Electricity Usage (Highest Usage Month: {highest_year_month_vehicle[0]}-{highest_year_month_vehicle[1]})', ax=ax2)
         ax2.set_ylim([0, df_highest_week_vehicle.groupby('Weekday')["max verbruik in kWh 2040"].sum().max()])
         
         # cols[1].pyplot(fig2)
         
         # Create the third chart
         fig3, ax3 = plt.subplots()
         df_weekly_highest_vehicle.plot(kind='area', stacked=True, 
                           title=f'Weekly Electricity Usage (Highest Usage Week: {highest_year_week_vehicle[0]}-Week {highest_year_week_vehicle[1]})', ax=ax3)
         ax3.set_ylim([0, df_highest_week_vehicle.groupby('Weekday')["max verbruik in kWh 2040"].sum().max()])

         
         # Create the fourth chart
         fig4, ax4 = plt.subplots()
         df_daily_highest_vehicle.plot(kind='area', stacked=True, 
                          title=f'Daily Electricity Usage (Highest Usage Day: {highest_year_month_day_vehicle[0]}-{highest_year_month_day_vehicle[1]}-{highest_year_month_day_vehicle[2]})', ax=ax4)
         ax4.set_ylim([0, df_highest_day_vehicle.groupby('Hour')["max verbruik in kWh 2040"].sum().max()])


         if show_line:
                  ax1.axhline(y=1500000 + adjustment_value, color='black', linestyle='--')
                  ax2.axhline(y=50000 + adjustment_value, color='black', linestyle='--')
                  ax3.axhline(y=40000 + adjustment_value, color='black', linestyle='--')
                  ax4.axhline(y=7500 + adjustment_value, color='black', linestyle='--')

         # Display the plots
         cols[0].pyplot(fig1)
         cols[1].pyplot(fig2)
         cols[2].pyplot(fig3)
         cols[3].pyplot(fig4)         

def main():
         page = st.sidebar.selectbox('Navigation', options=['Homepage', '1. Waar is de data op gebaseerd?', '2. Wat gebruikt wat?', '3. Wie gebruikt wat?'])
         
         if page == 'Homepage':
                  homepage()
         elif page == '1. Waar is de data op gebaseerd?':
                  bsg_page()
         elif page == '2. Wat gebruikt wat?':
                  vehicle_page()
         elif page == '3. Wie gebruikt wat?':
                  company_page()
         elif page == 'wat gebruikt wat? das2':
                  ffkijken()
        
if __name__ == "__main__":
         main()
