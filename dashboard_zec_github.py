import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd
import pydeck as pdk
st.set_page_config(layout="wide")

# Load the geopackage file
#df = pd.read_csv("df_final.csv")
df = pd.read_csv("test_df_bt.csv")
df_prob = pd.read_csv("df_prob.csv", index_col = 0)

df.columns = df.columns.str.lower()
df = df[["bedrijf", "werkt mee", "aantal truck", "aantal bakwagen", "aantal bestelwagen", 'truck gem afstand in km', 
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

def homepage():
         st.title('ZEC Mobility Dashboard')
         st.write('Dit dashboard geeft inzicht over het gebruik van elektriciteit op het bedrijventerrein Schiphol Trade Park. Met de transitie naar elektrische voertuigen zal er meer gevraagd worden van het netwerk. Door de ontwikkeling van de bedrijven en hun wagenpark in kaart te brengen kan er voorspeld worden hoe de stroomvraag zich ontwikkeld.')
         
         # The user can select a year
         year = st.selectbox('Select a year', options=[2025, 2030, 2035, 2040])
         
         # The user can select between maximum and average
         value_type = st.radio('Choose a value type', options=['max', 'gem'])
         
         # Based on the user's selections, choose the appropriate column
         if value_type:
                  usage_column = f'max verbruik in kWh {year}'
         else:
                  usage_column = f'gem verbruik in kWh {year}'
    

         @st.cache(allow_output_mutation=True)
         def load_data():
                  gdf = gpd.read_file("companies.gpkg")
                  # Convert to EPSG:4326
                  gdf = gdf.to_crs(epsg=4326)
                  gdf["lon"] = gdf["geometry"].x
                  gdf["lat"] = gdf["geometry"].y
                  return gdf

         data = load_data()
         
         df_map = df.groupby("Bedrijf")[usage_column].sum()
         data = data.merge(df_map, on = "Bedrijf", how = "left")
         data[usage_column] = (data[usage_column] - data[usage_column].min()) / (data[usage_column].max() - data[usage_column].min())
         
         test = pd.DataFrame([{"command": "st.selectbox", "rating": 4, "is_widget": True}, {"command": "st.balloons", "rating": 5, "is_widget": False},{"command": "st.time_input", "rating": 3, "is_widget": True}])
         edited_df = st.data_editor(test)
         
         favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
         st.markdown(f"Your favorite command is **{favorite_command}** 🎈")

    # Set the map's initial center to the mean of all points
         initial_view_state = pdk.ViewState(
                  latitude=data["lat"].mean(),
                  longitude=data["lon"].mean(),
                  zoom=13,
                  )

    # Create the scatter plot layer
         layer = pdk.Layer(
                  "ScatterplotLayer",
                  data,
                  get_position=["lon", "lat"],
                  get_radius= [usage_column],
                  radiusScale=10,
                  radiusUnits = "pixels",
                  get_fill_color=[180, 0, 200, 140],
                  )

    # Render the map
         st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=initial_view_state, map_style="mapbox://styles/mapbox/light-v9"))

    
    #### DATA
    
         #### YEAR
         df_yearly = df.groupby(['Year', 'Month'])[usage_column].sum()
         
         
         #### MONTH
         # Group by year, month and calculate the sum of 'Max verbruik in kWh 2040'
         df_monthly_total = df.groupby(['Year', 'Month'])[usage_column].sum().reset_index()
         
         # Find the month with the highest total usage
         highest_month = df_monthly_total[df_monthly_total[usage_column] == df_monthly_total[usage_column].max()]
         
         # Extract the year and month
         highest_year_month = highest_month[['Year', 'Month']].values[0]
         
         # Select data for the highest usage month
         df_highest_month = df[(df['Year'] == highest_year_month[0]) & (df['Month'] == highest_year_month[1])]
         
         # Group by day and 'werkt mee', and calculate the sum of 'Max verbruik in kWh 2040'
         df_monthly = df_highest_month.groupby('Day')[usage_column].sum()
         
         
         #### WEEK
         # Group by year, week and calculate the sum of 'Max verbruik in kWh 2040'
         df_weekly_total = df.groupby(['Year', 'Week'])[usage_column].sum().reset_index()
         
         # Find the week with the highest total usage
         highest_week = df_weekly_total[df_weekly_total[usage_column] == df_weekly_total[usage_column].max()]
         
         # Extract the year and week
         highest_year_week = highest_week[['Year', 'Week']].values[0]
         
         # Select data for the highest usage week
         df_highest_week = df[(df['Year'] == highest_year_week[0]) & (df['Week'] == highest_year_week[1])]
         
         # Group by weekday and 'werkt mee', and calculate the sum of 'Max verbruik in kWh 2040'
         df_weekly = df_highest_week.groupby('Weekday')[usage_column].sum()
         
         
         #### DAY
         # Group by year, month, day and calculate the sum of 'Max verbruik in kWh 2040'
         df_daily_total = df.groupby(['Year', 'Month', 'Day'])[usage_column].sum().reset_index()
         
         # Find the day with the highest total usage
         highest_day = df_daily_total[df_daily_total[usage_column] == df_daily_total[usage_column].max()]
         
         # Extract the year, month and day
         highest_year_month_day = highest_day[['Year', 'Month', 'Day']].values[0]
         
         # Select data for the highest usage day
         df_highest_day = df[(df['Year'] == highest_year_month_day[0]) & (df['Month'] == highest_year_month_day[1]) & (df['Day'] == highest_year_month_day[2])]
         
         # Group by hour and 'werkt mee', and calculate the sum of 'Max verbruik in kWh 2040'
         df_daily = df_highest_day.groupby('Hour')[usage_column].sum()
         
         
         
         
         
         #### PLOT
         # Create a 1x4 layout
         cols = st.columns(4)
         
         # Create the first chart
         fig1, ax1 = plt.subplots()
         df_yearly.plot(kind='area', stacked=True, title='Yearly Electricity Usage', ax=ax1)
         cols[0].pyplot(fig1)
         
         # Create the second chart
         fig2, ax2 = plt.subplots()
         df_monthly.plot(kind='area', stacked=True, 
                            title=f'Monthly Electricity Usage (Highest Usage Month: {highest_year_month[0]}-{highest_year_month[1]})', ax=ax2)
         cols[1].pyplot(fig2)
         
         # Create the third chart
         fig3, ax3 = plt.subplots()
         df_weekly.plot(kind='area', stacked=True, 
                           title=f'Weekly Electricity Usage (Highest Usage Week: {highest_year_week[0]}-Week {highest_year_week[1]})', ax=ax3)
         cols[2].pyplot(fig3)
         
         # Create the fourth chart
         fig4, ax4 = plt.subplots()
         df_daily.plot(kind='area', stacked=True, 
                          title=f'Daily Electricity Usage (Highest Usage Day: {highest_year_month_day[0]}-{highest_year_month_day[1]}-{highest_year_month_day[2]})', ax=ax4)
         cols[3].pyplot(fig4)


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
         col1, col2 = st.columns(2)
         
         # Place text in the left column
         col1.text("Your Text Here")  # Replace with your desired text

         show_line = st.checkbox('Capaciteit netwerk')
         
         # The user can select a year
         year = col1.selectbox('Select a year', options=[2025, 2030, 2035, 2040])
         
         # The user can select between maximum and average
         value_type = col1.radio('Choose a value type', options=['max', 'gem'])

         # Based on the user's selections, choose the appropriate column
         if value_type:
                  usage_column = f'max verbruik in kWh {year}'
         else:
                  usage_column = f'gem verbruik in kWh {year}'  


         


         
         # Create the pie chart for the right column
         labels = 'Werk niet mee', 'Werkt mee'
         explode = (0.1, 0)  # only "explode" the 2nd slice
         fig5, ax5 = plt.subplots(figsize=(2.5, 2.5))
         ax5.pie(df["werkt mee"].value_counts(), explode=explode, labels=labels, autopct='%1.1f%%', 
                 shadow=True, startangle=90)
         col2.pyplot(fig5)
    
         #### YEAR
         # Group by year, month and 'werkt mee', and calculate the sum of 'Max verbruik in kWh 2040'
         df_yearly_bet = df.groupby(['Year', 'Month', 'werkt mee'])[usage_column].sum().unstack()
         
         
         
         #### MONTH
         # Group by year, month and calculate the sum of 'Max verbruik in kWh 2040'
         df_monthly_total_bet = df.groupby(['Year', 'Month'])[usage_column].sum().reset_index()
         
         # Find the month with the highest total usage
         highest_month_bet = df_monthly_total_bet[df_monthly_total_bet[usage_column] == df_monthly_total_bet[usage_column].max()]
         
         # Extract the year and month
         highest_year_month_bet = highest_month_bet[['Year', 'Month']].values[0]
         
         # Select data for the highest usage month
         df_highest_month_bet = df[(df['Year'] == highest_year_month_bet[0]) & (df['Month'] == highest_year_month_bet[1])]
         
         # Group by day and 'werkt mee', and calculate the sum of 'Max verbruik in kWh 2040'
         df_monthly_bet = df_highest_month_bet.groupby(['Day', 'werkt mee'])[usage_column].sum().unstack()
         
         
         
         #### WEEK
         # Group by year, week and calculate the sum of 'Max verbruik in kWh 2040'
         df_weekly_total_bet = df.groupby(['Year', 'Week'])[usage_column].sum().reset_index()
         
         # Find the week with the highest total usage
         highest_week_bet = df_weekly_total_bet[df_weekly_total_bet[usage_column] == df_weekly_total_bet[usage_column].max()]
         
         # Extract the year and week
         highest_year_week_bet = highest_week_bet[['Year', 'Week']].values[0]
         
         # Select data for the highest usage week
         df_highest_week_bet = df[(df['Year'] == highest_year_week_bet[0]) & (df['Week'] == highest_year_week_bet[1])]
         
         # Group by weekday and 'werkt mee', and calculate the sum of 'Max verbruik in kWh 2040'
         df_weekly_bet = df_highest_week_bet.groupby(['Weekday', 'werkt mee'])[usage_column].sum().unstack()
         
         
         
         #### DAY
         # Group by year, month, day and calculate the sum of 'Max verbruik in kWh 2040'
         df_daily_total_bet = df.groupby(['Year', 'Month', 'Day'])[usage_column].sum().reset_index()
         
         # Find the day with the highest total usage
         highest_day_bet = df_daily_total_bet[df_daily_total_bet[usage_column] == df_daily_total_bet[usage_column].max()]
         
         # Extract the year, month and day
         highest_year_month_day_bet = highest_day_bet[['Year', 'Month', 'Day']].values[0]
         
         # Select data for the highest usage day
         df_highest_day_bet = df[(df['Year'] == highest_year_month_day_bet[0]) & (df['Month'] == highest_year_month_day_bet[1]) & (df['Day'] == highest_year_month_day_bet[2])]
         
         # Group by hour and 'werkt mee', and calculate the sum of 'Max verbruik in kWh 2040'
         df_daily_bet = df_highest_day_bet.groupby(['Hour', 'werkt mee'])[usage_column].sum().unstack()
         
         
         
         #### PLOT
         # Create a 1x4 layout
         cols = st.columns(4)
         
         # Create the first chart  
         fig1, ax1 = plt.subplots()
         df_yearly_bet.plot(kind='area', stacked=True, title='Yearly Electricity Usage', ax=ax1)

         ax1.set_ylim([0, df.groupby(['Year', 'Month'])["max verbruik in kWh 2040"].sum().max()])
         
         
         
         # if show_line:
         #         y_value = 1250000   Replace with the y value where you want the horizontal line
         #         ax1.axhline(y=y_value, color='red', linestyle='--')

         # cols[0].pyplot(fig1)
         
         
         # Create the second chart
         fig2, ax2 = plt.subplots()
         df_monthly_bet.plot(kind='area', stacked=True, 
                            title=f'Monthly Electricity Usage (Highest Usage Month: {highest_year_month_bet[0]}-{highest_year_month_bet[1]})', ax=ax2)
         ax2.set_ylim([0, df_highest_week_bet.groupby('Weekday')["max verbruik in kWh 2040"].sum().max()])
         #cols[1].pyplot(fig2)
         
         # Create the third chart
         fig3, ax3 = plt.subplots()
         df_weekly_bet.plot(kind='area', stacked=True, 
                           title=f'Weekly Electricity Usage (Highest Usage Week: {highest_year_week_bet[0]}-Week {highest_year_week_bet[1]})', ax=ax3)
         ax3.set_ylim([0, df_highest_week_bet.groupby('Weekday')["max verbruik in kWh 2040"].sum().max()])
         
         #cols[2].pyplot(fig3)
         
         # Create the fourth chart
         fig4, ax4 = plt.subplots()
         df_daily_bet.plot(kind='area', stacked=True, 
                          title=f'Daily Electricity Usage (Highest Usage Day: {highest_year_month_day_bet[0]}-{highest_year_month_day_bet[1]}-{highest_year_month_day_bet[2]})', ax=ax4)
         ax4.set_ylim([0, df_highest_day_bet.groupby('Hour')["max verbruik in kWh 2040"].sum().max()])
         #cols[3].pyplot(fig4)


         if show_line:
                  ax1.axhline(y=1500000, color='black', linestyle='--')
                  ax2.axhline(y=50000, color='black', linestyle='--')
                  ax3.axhline(y=40000, color='black', linestyle='--')
                  ax4.axhline(y=7500, color='black', linestyle='--')

         # Display the plots
         cols[0].pyplot(fig1)
         cols[1].pyplot(fig2)
         cols[2].pyplot(fig3)
         cols[3].pyplot(fig4)
         


    

    
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
         col1.text("Your Text Here")  # Replace with your desired text

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

         option = col2.selectbox('Choose data to display', ['Voertuigen', 'Individual Vehicle Types'])
         
         if option == 'Voertuigen':
             columns_to_display = ['pand', 'voertuigen']
         else:
             columns_to_display = ['pand', 'truck', 'bakwagen', 'bestelwagen']
         
         # Plotting
         fig5, ax5 = plt.subplots(figsize=())
         toename_df[columns_to_display].plot(kind='area', stacked=True, title=f'Toename piek stroomnet', ax=ax5)
         col2.pyplot(fig5)



         
         
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



def main():
         page = st.sidebar.selectbox('Navigation', options=['Homepage', 'Waar is de data op gebaseerd?', 'Wat gebruikt wat?', 'Wie gebruikt wat?'])
         
         if page == 'Homepage':
                  homepage()
         elif page == 'Waar is de data op gebaseerd?':
                  bsg_page()
         elif page == 'Wat gebruikt wat?':
                  vehicle_page()
         elif page == 'Wie gebruikt wat?':
                  company_page()
        
if __name__ == "__main__":
         main()
