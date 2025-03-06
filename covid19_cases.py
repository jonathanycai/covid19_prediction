import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

from fbprophet import Prophet
from sklearn.metrics import r2_score

plt.style.use("ggplot")

# import data
df0 = pd.read_csv("data/CONVENIENT_global_confirmed_cases.csv")
df1 = pd.read_csv("data/CONVENIENT_global_deaths.csv")

world = pd.DataFrame({"Country": [], "Cases": []})
world["Country"] = df0.iloc[:, 1:].columns

# compute total cases per country
cases = []
for i in world["Country"]:
    cases.append(pd.to_numeric(df0[i][1:]).sum())
world["Cases"] = cases

# combines data for same country but different name [USA and USA.]
country_list = list(world["Country"].values)
idx = 0
for i in country_list:
    sayac = 0
    for j in i:
        if j == ".":
            i = i[:sayac]
            country_list[idx] = i
        elif j == "(":
            i = i[:sayac - 1]
            country_list[idx] = i
        else:
            sayac += 1
    idx += 1

world["Country"] = country_list
world = world.groupby("Country")["Cases"].sum().reset_index()
print(world.head())  # Debugging output

continent = pd.read_csv("data/continents2.csv")
continent["name"] = continent["name"].str.upper()
print(continent.head())  # Debugging output

# categorizes countries into bins based on total number of cases
world["Cases Range"] = pd.cut(
    world["Cases"],
    [-150000, 50000, 200000, 800000, 1500000, 15000000],
    labels=["U50K", "50Kto200K", "200Kto800K", "800Kto1.5M", "1.5M+"]
)
alpha = []

# adds names in alpha-3 [Canada -> CAN]
for i in world["Country"].str.upper().values:
    if i == "BRUNEI":
        i = "BRUNEI DARUSSALAM"
    elif i == "US":
        i = "UNITED STATES"
    if len(continent[continent["name"] == i]["alpha-3"].values) == 0:
        alpha.append(np.nan)
    else:
        alpha.append(continent[continent["name"] == i]["alpha-3"].values[0])

world["Alpha3"] = alpha
print(world.head())  # Debugging output

fig = px.choropleth(
    world.dropna(),
    locations="Alpha3",
    color="Cases Range",
    projection="natural earth",
    color_discrete_sequence=["white", "khaki", "yellow", "orange", "red"]
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()