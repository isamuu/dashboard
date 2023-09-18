import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd
import pydeck as pdk
from plotly.tools import mpl_to_plotly

st.set_page_config(layout="wide")

# Load the geopackage file
#df = pd.read_csv("df_final.csv")
df = pd.read_csv("test_df_bt.csv")
df_prob = pd.read_csv("df_prob.csv", index_col = 0)

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



# dataframe maken voor tijden
tijdrange = pd.DataFrame(pd.date_range("01-01-2022", "01-01-2023", freq = "H"))
tijdrange["Maand nummer"] = tijdrange[0].dt.month
tijdrange["Dag nummer"] = tijdrange[0].dt.dayofweek
tijdrange["Dag nummer"] = tijdrange["Dag nummer"]+1
tijdrange["Uur nummer"] = tijdrange[0].dt.hour
tijdrange = tijdrange.rename(columns = {0:"Datum"})

df_gebruik = df_prob.merge(tijdrange, on = ["Maand nummer", "Dag nummer", "Uur nummer"])
df_gebruik = df_gebruik.sort_values(["Bedrijf", "Datum"]).reset_index(drop = True)
df_gebruik["Probability"] = df_gebruik["Probability Maand"]*df_gebruik["Probability Dag"]*df_gebruik["Probability Uur"]
df_gebruik = df_gebruik[["Bedrijf", "Datum", "Probability"]].merge(df, left_on = "Bedrijf", right_on = "bedrijf", how = "left")
df_gebruik = df_gebruik.fillna(0)

# voor maximaal aantal km
# afstand*aantal voertuigen*verbruik per km
df_gebruik["truck max verbruik 2025 in kWh"] = df_gebruik['truck max afstand in km'] * df_gebruik['truck 2025'] * 1  * df_gebruik["Probability"]
df_gebruik["bakwagen max verbruik 2025 in kWh"] = df_gebruik['bakwagen max afstand in km'] * df_gebruik['bakwagen 2025'] * 0.9 * df_gebruik["Probability"]
df_gebruik["bestelwagen max verbruik 2025 in kWh"] = df_gebruik['bestelwagen max afstand in km'] * df_gebruik['bestelwagen 2025'] * 0.2 * df_gebruik["Probability"]
df_gebruik["voertuigen max verbruik 2025 in kWh"] = df_gebruik["truck max verbruik 2025 in kWh"] + df_gebruik["bakwagen max verbruik 2025 in kWh"] + df_gebruik["bestelwagen max verbruik 2025 in kWh"]

df_gebruik["truck max verbruik 2030 in kWh"] = df_gebruik['truck max afstand in km'] * df_gebruik['truck 2030'] * 1  * df_gebruik["Probability"]
df_gebruik["bakwagen max verbruik 2030 in kWh"] = df_gebruik['bakwagen max afstand in km'] * df_gebruik['bakwagen 2030'] * 0.9 * df_gebruik["Probability"]
df_gebruik["bestelwagen max verbruik 2030 in kWh"] = df_gebruik['bestelwagen max afstand in km'] * df_gebruik['bestelwagen 2030'] * 0.2 * df_gebruik["Probability"]
df_gebruik["voertuigen max verbruik 2030 in kWh"] = df_gebruik["truck max verbruik 2030 in kWh"] + df_gebruik["bakwagen max verbruik 2030 in kWh"] + df_gebruik["bestelwagen max verbruik 2030 in kWh"]

df_gebruik["truck max verbruik 2035 in kWh"] = df_gebruik['truck max afstand in km'] * df_gebruik['truck 2035'] * 1  * df_gebruik["Probability"]
df_gebruik["bakwagen max verbruik 2035 in kWh"] = df_gebruik['bakwagen max afstand in km'] * df_gebruik['bakwagen 2035'] * 0.9 * df_gebruik["Probability"]
df_gebruik["bestelwagen max verbruik 2035 in kWh"] = df_gebruik['bestelwagen max afstand in km'] * df_gebruik['bestelwagen 2035'] * 0.2 * df_gebruik["Probability"]
df_gebruik["voertuigen max verbruik 2035 in kWh"] = df_gebruik["truck max verbruik 2035 in kWh"] + df_gebruik["bakwagen max verbruik 2035 in kWh"] + df_gebruik["bestelwagen max verbruik 2035 in kWh"]

df_gebruik["truck max verbruik 2040 in kWh"] = df_gebruik['truck max afstand in km'] * df_gebruik['truck 2040'] * 1  * df_gebruik["Probability"]
df_gebruik["bakwagen max verbruik 2040 in kWh"] = df_gebruik['bakwagen max afstand in km'] * df_gebruik['bakwagen 2040'] * 0.9 * df_gebruik["Probability"]
df_gebruik["bestelwagen max verbruik 2040 in kWh"] = df_gebruik['bestelwagen max afstand in km'] * df_gebruik['bestelwagen 2040'] * 0.2 * df_gebruik["Probability"]
df_gebruik["voertuigen max verbruik 2040 in kWh"] = df_gebruik["truck max verbruik 2040 in kWh"] + df_gebruik["bakwagen max verbruik 2040 in kWh"] + df_gebruik["bestelwagen max verbruik 2040 in kWh"]

# voor gemiddeld aantal km
df_gebruik["truck gem verbruik 2025 in kWh"] = df_gebruik['truck gem afstand in km'] * df_gebruik['truck 2025'] * 1  * df_gebruik["Probability"]
df_gebruik["bakwagen gem verbruik 2025 in kWh"] = df_gebruik['bakwagen gem afstand in km'] * df_gebruik['bakwagen 2025'] * 0.9 * df_gebruik["Probability"]
df_gebruik["bestelwagen gem verbruik 2025 in kWh"] = df_gebruik['bestelwagen gem afstand in km'] * df_gebruik['bestelwagen 2025'] * 0.2 * df_gebruik["Probability"]
df_gebruik["voertuigen gem verbruik 2025 in kWh"] = df_gebruik["truck gem verbruik 2025 in kWh"] + df_gebruik["bakwagen gem verbruik 2025 in kWh"] + df_gebruik["bestelwagen gem verbruik 2025 in kWh"]

df_gebruik["truck gem verbruik 2030 in kWh"] = df_gebruik['truck gem afstand in km'] * df_gebruik['truck 2030'] * 1  * df_gebruik["Probability"]
df_gebruik["bakwagen gem verbruik 2030 in kWh"] = df_gebruik['bakwagen gem afstand in km'] * df_gebruik['bakwagen 2030'] * 0.9 * df_gebruik["Probability"]
df_gebruik["bestelwagen gem verbruik 2030 in kWh"] = df_gebruik['bestelwagen gem afstand in km'] * df_gebruik['bestelwagen 2030'] * 0.2 * df_gebruik["Probability"]
df_gebruik["voertuigen gem verbruik 2030 in kWh"] = df_gebruik["truck gem verbruik 2030 in kWh"] + df_gebruik["bakwagen gem verbruik 2030 in kWh"] + df_gebruik["bestelwagen gem verbruik 2030 in kWh"]

df_gebruik["truck gem verbruik 2035 in kWh"] = df_gebruik['truck gem afstand in km'] * df_gebruik['truck 2035'] * 1  * df_gebruik["Probability"]
df_gebruik["bakwagen gem verbruik 2035 in kWh"] = df_gebruik['bakwagen gem afstand in km'] * df_gebruik['bakwagen 2035'] * 0.9 * df_gebruik["Probability"]
df_gebruik["bestelwagen gem verbruik 2035 in kWh"] = df_gebruik['bestelwagen gem afstand in km'] * df_gebruik['bestelwagen 2035'] * 0.2 * df_gebruik["Probability"]
df_gebruik["voertuigen gem verbruik 2035 in kWh"] = df_gebruik["truck gem verbruik 2035 in kWh"] + df_gebruik["bakwagen gem verbruik 2035 in kWh"] + df_gebruik["bestelwagen gem verbruik 2035 in kWh"]

df_gebruik["truck gem verbruik 2040 in kWh"] = df_gebruik['truck gem afstand in km'] * df_gebruik['truck 2040'] * 1  * df_gebruik["Probability"]
df_gebruik["bakwagen gem verbruik 2040 in kWh"] = df_gebruik['bakwagen gem afstand in km'] * df_gebruik['bakwagen 2040'] * 0.9 * df_gebruik["Probability"]
df_gebruik["bestelwagen gem verbruik 2040 in kWh"] = df_gebruik['bestelwagen gem afstand in km'] * df_gebruik['bestelwagen 2040'] * 0.2 * df_gebruik["Probability"]
df_gebruik["voertuigen gem verbruik 2040 in kWh"] = df_gebruik["truck gem verbruik 2040 in kWh"] + df_gebruik["bakwagen gem verbruik 2040 in kWh"] + df_gebruik["bestelwagen gem verbruik 2040 in kWh"]

#Probability bepalen voor verdeling van jaarverbruik over de dagen
jaarverbruik = tijdrange
# Filter the dataframe based on the conditions
filtered_df = jaarverbruik[(jaarverbruik['Dag nummer'].between(1, 5)) & (jaarverbruik['Uur nummer'].between(7, 17))]

# Create a new column in the original dataframe, initially with all zeros
jaarverbruik['Jaarverbruik Probability'] = 0

# Assign the computed value to the filtered rows in the new column
jaarverbruik.loc[filtered_df.index, 'Jaarverbruik Probability'] = 1/len(filtered_df)
jaarverbruik = jaarverbruik[["Datum", "Jaarverbruik Probability"]]

df_final = df_gebruik.merge(jaarverbruik, on = "Datum").sort_values(["Bedrijf", "Datum"])
df_final = df_final.sort_values(by = ["Bedrijf", "Datum"])
df_final["Verbruik pand in kWh"] = df_final["jaarverbruik"]*df_final["Jaarverbruik Probability"]

df_final["Gem verbruik in kWh 2025"] = df_final["Verbruik pand in kWh"] + df_final["voertuigen gem verbruik 2025 in kWh"]
df_final["Gem verbruik in kWh 2030"] = df_final["Verbruik pand in kWh"] + df_final["voertuigen gem verbruik 2030 in kWh"]
df_final["Gem verbruik in kWh 2035"] = df_final["Verbruik pand in kWh"] + df_final["voertuigen gem verbruik 2035 in kWh"]
df_final["Gem verbruik in kWh 2040"] = df_final["Verbruik pand in kWh"] + df_final["voertuigen gem verbruik 2040 in kWh"]

df_final["Max verbruik in kWh 2025"] = df_final["Verbruik pand in kWh"] + df_final["voertuigen max verbruik 2025 in kWh"]
df_final["Max verbruik in kWh 2030"] = df_final["Verbruik pand in kWh"] + df_final["voertuigen max verbruik 2030 in kWh"]
df_final["Max verbruik in kWh 2035"] = df_final["Verbruik pand in kWh"] + df_final["voertuigen max verbruik 2035 in kWh"]
df_final["Max verbruik in kWh 2040"] = df_final["Verbruik pand in kWh"] + df_final["voertuigen max verbruik 2040 in kWh"]

df = df_final

# Set to datetime type
df['Datum'] = pd.to_datetime(df['Datum'])
# Extract year and month from 'Datum'
df['Year'] = df['Datum'].dt.year
df['Month'] = df['Datum'].dt.month
df['Day'] = df['Datum'].dt.day
df['Week'] = df['Datum'].dt.isocalendar().week
df['Weekday'] = df['Datum'].dt.weekday
df['Hour'] = df['Datum'].dt.hour
df = df[df['Year'] == 2022]
df = df.rename(columns = {'Gem verbruik in kWh 2025':'gem verbruik in kWh 2025','Gem verbruik in kWh 2030':'gem verbruik in kWh 2030', 'Gem verbruik in kWh 2035':'gem verbruik in kWh 2035', 'Gem verbruik in kWh 2040':'gem verbruik in kWh 2040', 'Max verbruik in kWh 2025':'max verbruik in kWh 2025', 'Max verbruik in kWh 2030':'max verbruik in kWh 2030', 'Max verbruik in kWh 2035':'max verbruik in kWh 2035', 'Max verbruik in kWh 2040':'max verbruik in kWh 2040'})

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
         aantal_bakwagen = int(df[df["Datum"]=="2022-01-01 00:00:00"]["aantal bakwagen"].sum())
         icon_bakwagen_html = f'''<img src="{icon_bakwagen}" width="150" style="display: block; margin: auto;">'
         <p style="text-align: center; font-size: 24px;">{aantal_bakwagen} Bakwagens</p>'''
         
         icon_bestelwagen = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bestelwagen.jpg"
         aantal_bestelwagen = int(df[df["Datum"]=="2022-01-01 00:00:00"]["aantal bestelwagen"].sum())
         icon_bestelwagen_html = f'''<img src="{icon_bestelwagen}" width="150" style="display: block; margin: auto;">'
         <p style="text-align: center; font-size: 24px;">{aantal_bestelwagen} Bestelwagens</p>'''
         
         icon_truck = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20truck.jpg"
         aantal_truck = int(df[df["Datum"]=="2022-01-01 00:00:00"]["aantal truck"].sum())
         icon_truck_html = f'''<img src="{icon_truck}" width="150" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 24px;">{aantal_truck} Trucks</p>'''
         
         icon_bedrijf = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bedrijf.jpg"
         aantal_bedrijf = len(df['Bedrijf'].unique())
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

         text1, text2 = st.columns([0.4,0.5])

         text1.write(""" \n\n\n\nDit dashboard geeft inzicht over het gebruik van elektriciteit op het bedrijventerrein Schiphol Trade Park. 
         Met de transitie naar elektrische voertuigen zal er meer gevraagd worden van het netwerk. 
         Door de ontwikkeling van de bedrijven en hun wagenpark in kaart te brengen kan er voorspeld worden hoe de stroomvraag zich ontwikkeld.
         
         \n\n Terwijl de wereld zich richt op duurzame energie, wordt de overstap naar elektrische voertuigen op bedrijventerreinen een groot en complex vraagstuk. 
         Het is algemeen bekend dat de elektriciteitsinfrastructuur in Nederland op sommige locaties al tegen zijn uiterste loopt.
         De transitie naar eleketrisch transport zal nog meer druk zetten op onze infrastructuur, zo ook op het bedrijventerrein Schiphol Trade Park.
         Dit betekent dat we geconfronteerd worden met een complexe puzzel die op de juiste manier moet worden aangepakt. 
         Dit dashboard biedt inzichten in de huidige situatie, uitdagingen en kansen binnen op het Schiphol Trade Park. \n\n\n\n""")
         
         
         column0, column1, column2, column3, column4, column5 = st.columns([0.2,0.2,0.2,0.2,0.1,0.3])


         #Bedrijven
         icon_bedrijf = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bedrijf.jpg"
         aantal_bedrijf = len(df['Bedrijf'].unique())
         icon_bedrijf_html = f'''<img src="{icon_bedrijf}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bedrijf} Bedrijven</p>'''    
         column0.markdown(icon_bedrijf_html, unsafe_allow_html=True)

         icon_bedrijf_goud = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bedrijf%20goud.jpg"
         aantal_bedrijf_goud = len(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Goud")]["Bedrijf"])
         icon_bedrijf_goud_html = f'''<img src="{icon_bedrijf_goud}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bedrijf_goud} Bedrijven</p>'''    
         column0.markdown(icon_bedrijf_goud_html, unsafe_allow_html=True)

         icon_bedrijf_zilver = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bedrijf%20zilver.jpg"
         aantal_bedrijf_zilver = len(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Zilver")]["Bedrijf"])
         icon_bedrijf_zilver_html = f'''<img src="{icon_bedrijf_zilver}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bedrijf_zilver} Bedrijven</p>'''    
         column0.markdown(icon_bedrijf_zilver_html, unsafe_allow_html=True)

         icon_bedrijf_brons = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bedrijf%20brons.jpg"
         aantal_bedrijf_brons = len(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Brons")]["Bedrijf"])
         icon_bedrijf_brons_html = f'''<img src="{icon_bedrijf_brons}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bedrijf_brons} Bedrijven</p>'''    
         column0.markdown(icon_bedrijf_brons_html, unsafe_allow_html=True)
         
         

         #TRUCK
         icon_truck = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20truck.jpg"
         aantal_truck = int(df[df["Datum"]=="2022-01-01 00:00:00"]["aantal truck"].sum())
         icon_truck_html = f'''<img src="{icon_truck}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_truck} Truck</p>'''
         column1.markdown(icon_truck_html, unsafe_allow_html=True)

         icon_truck_goud = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20truck%20goud.jpg"
         aantal_truck_goud = int(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Goud")]["aantal truck"].sum())
         icon_truck_goud_html = f'''<img src="{icon_truck_goud}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_truck_goud} Truck</p>'''
         column1.markdown(icon_truck_goud_html, unsafe_allow_html=True)
         
         icon_truck_zilver = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20truck%20zilver.jpg"
         aantal_truck_zilver = int(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Zilver")]["aantal truck"].sum())
         icon_truck_zilver_html = f'''<img src="{icon_truck_zilver}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_truck_zilver} Truck</p>'''
         column1.markdown(icon_truck_zilver_html, unsafe_allow_html=True)

         icon_truck_brons = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20truck%20brons.jpg"
         aantal_truck_brons = int(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Brons")]["aantal truck"].sum())
         icon_truck_brons_html = f'''<img src="{icon_truck_brons}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_truck_brons} Truck</p>'''
         column1.markdown(icon_truck_brons_html, unsafe_allow_html=True)

         #BAKWAGEN
         icon_bakwagen = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bakwagen.jpg"
         aantal_bakwagen = int(df[df["Datum"]=="2022-01-01 00:00:00"]["aantal bakwagen"].sum())
         icon_bakwagen_html = f'''<img src="{icon_bakwagen}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bakwagen} Bakwagens</p>'''
         column2.markdown(icon_bakwagen_html, unsafe_allow_html=True)

         icon_bakwagen_goud = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bakwagen%20goud.jpg"
         aantal_bakwagen_goud = int(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Goud")]["aantal bakwagen"].sum())
         icon_bakwagen_goud_html = f'''<img src="{icon_bakwagen_goud}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bakwagen_goud} Bakwagens</p>'''
         column2.markdown(icon_bakwagen_goud_html, unsafe_allow_html=True)
         
         icon_bakwagen_zilver = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bakwagen%20zilver.jpg"
         aantal_bakwagen_zilver = int(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Zilver")]["aantal bakwagen"].sum())
         icon_bakwagen_zilver_html = f'''<img src="{icon_bakwagen_zilver}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bakwagen_zilver} Bakwagens</p>'''
         column2.markdown(icon_bakwagen_zilver_html, unsafe_allow_html=True)

         icon_bakwagen_brons = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bakwagen%20brons.jpg"
         aantal_bakwagen_brons = int(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Brons")]["aantal bakwagen"].sum())
         icon_bakwagen_brons_html = f'''<img src="{icon_bakwagen_brons}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bakwagen_brons} bakwagen</p>'''
         column2.markdown(icon_bakwagen_brons_html, unsafe_allow_html=True)


         #BESTELWAGEN
         icon_bestelwagen = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bestelwagen.jpg"
         aantal_bestelwagen = int(df[df["Datum"]=="2022-01-01 00:00:00"]["aantal bestelwagen"].sum())
         icon_bestelwagen_html = f'''<img src="{icon_bestelwagen}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bestelwagen} bestelwagen</p>'''
         column3.markdown(icon_bestelwagen_html, unsafe_allow_html=True)

         icon_bestelwagen_goud = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bestelwagen%20goud.jpg"
         aantal_bestelwagen_goud = int(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Goud")]["aantal bestelwagen"].sum())
         icon_bestelwagen_goud_html = f'''<img src="{icon_bestelwagen_goud}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bestelwagen_goud} bestelwagen</p>'''
         column3.markdown(icon_bestelwagen_goud_html, unsafe_allow_html=True)
         
         icon_bestelwagen_zilver = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bestelwagen%20zilver.jpg"
         aantal_bestelwagen_zilver = int(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Zilver")]["aantal bestelwagen"].sum())
         icon_bestelwagen_zilver_html = f'''<img src="{icon_bestelwagen_zilver}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bestelwagen_zilver} bestelwagen</p>'''
         column3.markdown(icon_bestelwagen_zilver_html, unsafe_allow_html=True)

         icon_bestelwagen_brons = "https://raw.githubusercontent.com/isamuu/dashboard/main/Icons%20dashboard/db%20bestelwagen%20brons.jpg"
         aantal_bestelwagen_brons = int(df[(df["Datum"]=="2022-01-01 00:00:00") & (df["kwaliteit data"] == "Brons")]["aantal bestelwagen"].sum())
         icon_bestelwagen_brons_html = f'''<img src="{icon_bestelwagen_brons}" width="100" style="display: block; margin: auto;">
         <p style="text-align: center; font-size: 18px;">{aantal_bestelwagen_brons} bestelwagen</p>'''
         column3.markdown(icon_bestelwagen_brons_html, unsafe_allow_html=True)



         


         #show_line = st.checkbox('Capaciteit netwerk')
         
         # The user can select a year
         #year = column2.selectbox('Select a year', options=[2025, 2030, 2035, 2040])
         
         # The user can select between maximum and average
         #value_type = column3.radio('Choose a value type', options=['max', 'gem'])

         # Based on the user's selections, choose the appropriate column
         #if value_type:
         #         usage_column = f'max verbruik in kWh {year}'
         #else:
         #         usage_column = f'gem verbruik in kWh {year}'  


         # Create a dataframe
         df_voertuigen = df[df["Datum"]=="2022-01-01 00:00:00"][['kwaliteit data', 'aantal truck', 'aantal bakwagen', 'aantal bestelwagen']]
         df_voertuigen = df_voertuigen.groupby(by = "kwaliteit data").sum()
         df_voertuigen["aantal"] = df_voertuigen['aantal truck'] + df_voertuigen['aantal bakwagen'] + df_voertuigen['aantal bestelwagen']
         df_voertuigen = df_voertuigen.reindex(['Goud', 'Zilver', 'Brons'])
         
         labels = df_voertuigen.index.tolist()
         colors = ['gold', 'silver', '#cd7f32']  # gold, silver, bronze colors
         explode = (0.5, 0.25, 0)  # explode only the gold slice
         fig5, ax5 = plt.subplots(figsize=(2.5, 2.5))
         ax5.pie(df_voertuigen['aantal'], explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
         column5.pyplot(fig5)
         column5.write('De bovenstaande grafiek geeft weer dat een groot deel van het aantal voertuigen bestaat uit de geschatte data)
                  


         


    
         #### YEAR
         # Group by year, month and 'werkt mee', and calculate the sum of 'Max verbruik in kWh 2040'
         #df_yearly_bet = df.groupby(['Year', 'Month', 'werkt mee'])[usage_column].sum().unstack()
         
         
         
         #### MONTH
         # Group by year, month and calculate the sum of 'Max verbruik in kWh 2040'
         #df_monthly_total_bet = df.groupby(['Year', 'Month'])[usage_column].sum().reset_index()
         
         # Find the month with the highest total usage
         #highest_month_bet = df_monthly_total_bet[df_monthly_total_bet[usage_column] == df_monthly_total_bet[usage_column].max()]
         
         # Extract the year and month
         #highest_year_month_bet = highest_month_bet[['Year', 'Month']].values[0]
         
         # Select data for the highest usage month
         #df_highest_month_bet = df[(df['Year'] == highest_year_month_bet[0]) & (df['Month'] == highest_year_month_bet[1])]
         
         # Group by day and 'werkt mee', and calculate the sum of 'Max verbruik in kWh 2040'
         #df_monthly_bet = df_highest_month_bet.groupby(['Day', 'werkt mee'])[usage_column].sum().unstack()
         
         
         
         #### WEEK
         # Group by year, week and calculate the sum of 'Max verbruik in kWh 2040'
         #df_weekly_total_bet = df.groupby(['Year', 'Week'])[usage_column].sum().reset_index()
         
         # Find the week with the highest total usage
         #highest_week_bet = df_weekly_total_bet[df_weekly_total_bet[usage_column] == df_weekly_total_bet[usage_column].max()]
         
         # Extract the year and week
         #highest_year_week_bet = highest_week_bet[['Year', 'Week']].values[0]
         
         # Select data for the highest usage week
         #df_highest_week_bet = df[(df['Year'] == highest_year_week_bet[0]) & (df['Week'] == highest_year_week_bet[1])]
         
         # Group by weekday and 'werkt mee', and calculate the sum of 'Max verbruik in kWh 2040'
         #df_weekly_bet = df_highest_week_bet.groupby(['Weekday', 'werkt mee'])[usage_column].sum().unstack()
         
         
         
         #### DAY
         # Group by year, month, day and calculate the sum of 'Max verbruik in kWh 2040'
         #df_daily_total_bet = df.groupby(['Year', 'Month', 'Day'])[usage_column].sum().reset_index()
         
         # Find the day with the highest total usage
         #highest_day_bet = df_daily_total_bet[df_daily_total_bet[usage_column] == df_daily_total_bet[usage_column].max()]
         
         # Extract the year, month and day
         #highest_year_month_day_bet = highest_day_bet[['Year', 'Month', 'Day']].values[0]
         
         # Select data for the highest usage day
         #df_highest_day_bet = df[(df['Year'] == highest_year_month_day_bet[0]) & (df['Month'] == highest_year_month_day_bet[1]) & (df['Day'] == highest_year_month_day_bet[2])]
         
         # Group by hour and 'werkt mee', and calculate the sum of 'Max verbruik in kWh 2040'
         #df_daily_bet = df_highest_day_bet.groupby(['Hour', 'werkt mee'])[usage_column].sum().unstack()
         
         
         
         #### PLOT
         # Create a 1x4 layout
        # cols = st.columns(4)
         
         # Create the first chart  
         #fig1, ax1 = plt.subplots()
         #df_yearly_bet.plot(kind='area', stacked=True, title='Yearly Electricity Usage', ax=ax1)

        # ax1.set_ylim([0, df.groupby(['Year', 'Month'])["max verbruik in kWh 2040"].sum().max()])
         
         
         
         # if show_line:
         #         y_value = 1250000   Replace with the y value where you want the horizontal line
         #         ax1.axhline(y=y_value, color='red', linestyle='--')

         # cols[0].pyplot(fig1)
         
         
         # Create the second chart
         #fig2, ax2 = plt.subplots()
         #df_monthly_bet.plot(kind='area', stacked=True, 
         #                   title=f'Monthly Electricity Usage (Highest Usage Month: {highest_year_month_bet[0]}-{highest_year_month_bet[1]})', ax=ax2)
         #ax2.set_ylim([0, df_highest_week_bet.groupby('Weekday')["max verbruik in kWh 2040"].sum().max()])
         #cols[1].pyplot(fig2)
         
         # Create the third chart
         #fig3, ax3 = plt.subplots()
         #df_weekly_bet.plot(kind='area', stacked=True, 
         #                  title=f'Weekly Electricity Usage (Highest Usage Week: {highest_year_week_bet[0]}-Week {highest_year_week_bet[1]})', ax=ax3)
         #ax3.set_ylim([0, df_highest_week_bet.groupby('Weekday')["max verbruik in kWh 2040"].sum().max()])
         
         #cols[2].pyplot(fig3)
         
         # Create the fourth chart
         #fig4, ax4 = plt.subplots()
         #df_daily_bet.plot(kind='area', stacked=True, 
         #                 title=f'Daily Electricity Usage (Highest Usage Day: {highest_year_month_day_bet[0]}-{highest_year_month_day_bet[1]}-{highest_year_month_day_bet[2]})', ax=ax4)
         #ax4.set_ylim([0, df_highest_day_bet.groupby('Hour')["max verbruik in kWh 2040"].sum().max()])
         #cols[3].pyplot(fig4)


         #if show_line:
         #         ax1.axhline(y=1500000, color='black', linestyle='--')
         #         ax2.axhline(y=50000, color='black', linestyle='--')
         #         ax3.axhline(y=40000, color='black', linestyle='--')
                #  ax4.axhline(y=7500, color='black', linestyle='--')

         # Display the plots
         #cols[0].pyplot(fig1)
         #cols[1].pyplot(fig2)
         #cols[2].pyplot(fig3)
         #cols[3].pyplot(fig4)
         


    

    
def vehicle_page(): 
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
         col1.text(""" Dit dashboard geeft inzicht over het gebruik van elektriciteit op het bedrijventerrein Schiphol Trade Park. 
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
        
if __name__ == "__main__":
         main()
