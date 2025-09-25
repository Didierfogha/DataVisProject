from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
import json
import requests
import os
import logging
from django.conf import settings
import pandas as pd
from .functions import *
import pandas as pd
import json

log = logging.getLogger(__name__)

excel_path = os.path.join(settings.BASE_DIR, 'data', 'data.xlsx')

df = pd.read_excel(excel_path, header=2)

cols = list(df.columns)
list_cont = df[cols[4]].unique()
options_cont = []

pays_par_continent = []

cont_ = []
num_pays = []

for continent in list_cont:
    #list_pays = df[cols[4] == continent][cols[7]].unique()
    options_cont.append(
        {'label': continent, 'value': continent}
    )

    pays_par_continent.append(
        {
            'label': continent, 'value': list(df[df[cols[4]] == continent][cols[7]].unique())
        }
    )
    list_pays = df[df[cols[4]] == continent][cols[7]].unique()

# 🔁 Conversion de liste en dictionnaire
region_pays_dict = {item['label']: item['value'] for item in pays_par_continent}


# Valeur initiale
initial_region = options_cont[0]['value']
initial_country = region_pays_dict[initial_region][0]
initial_sex = df[cols[12]].unique()[0]

nombre_lignes = df.shape[0]
titre = df[cols[1]].unique()

ttr = compare_expectancies(titre[0], titre[1])

result1 = short_compare(titre[0], titre[1])

app_dropdown = [{'label': x, 'value': x} for x in df[cols[1]].unique()]

app_sexe = [{'label': c, 'value': c} for c in df[cols[12]].unique()]


def get_continent_data(result, continent_name):
    """
    Filtrer la structure JSON pour ne garder que le continent demandé
    """
    return next((item for item in result if item["Continent"] == continent_name), None)


def compute_mean(data):
    """
    Prend une liste de dictionnaires (avec 'continent', 'country', 'code', 'year', 'value')
    et retourne une liste de dicts avec la moyenne arrondie à une décimale.
    """
    df = pd.DataFrame(data)

    result = (
        df.groupby(["continent", "country", "code"], as_index=False)["value"]
          .mean()
          .rename(columns={"value": "value"})
    )

    # ✅ arrondir à une décimale
    result["value"] = result["value"].round(1)

    return result.to_dict(orient="records")

def home(request):
    filt_df = df[df[cols[1]] == titre[0]]

    col1s = list(filt_df.columns)

    l_cont = filt_df[cols[4]].unique()

    xr = {}
    xr1 = {}
    nodes = []
    links = []

    for region in l_cont:
        filtered_df = filt_df[filt_df[cols[4]] == region]

        # Moyenne par année
        moyennes = filtered_df.groupby("Period")["FactValueNumeric"].mean().reset_index()

        # Arrondir à 1 chiffre après la virgule
        moyennes["FactValueNumeric"] = moyennes["FactValueNumeric"].round(1)

        # Conversion en liste de dicts
        result = moyennes.to_dict(orient="records")

        # Moyenne par année
        moyennes1 = filtered_df.groupby("Dim1")["FactValueNumeric"].mean().reset_index()

        # Arrondir à 1 chiffre après la virgule
        moyennes1["FactValueNumeric"] = moyennes1["FactValueNumeric"].round(1)

        # Conversion en liste de dicts
        result11 = moyennes1.to_dict(orient="records")

        xr[region] = result
        xr1[region] = result11

        liste_de_pays = filtered_df[filtered_df[cols[4]] == region][cols[7]].unique()


        nodes.append({'id': region, 'type': "continent"})
        for pays in liste_de_pays:
            nodes.append({"id":pays, "type":"country"},)
            links.append({'source': region, 'target': pays})


    results1 = []

    for region, values in xr.items():
        for entry in values:
            results1.append({
                "region": region,
                "year": entry["Period"],
                "value": entry["FactValueNumeric"]
            })

    results55 = []

    for region, values in xr1.items():
        for entry in values:
            results55.append({
                "region": region,
                "sex": entry["Dim1"],
                "value": entry["FactValueNumeric"]
            })


    rr = []
    rr1 = []

    for index, row in filt_df.iterrows():
        rr.append(
            {'region': row[cols[4]], 'year': row[cols[9]], 'value': row[cols[23]]}
        )
        rr1.append(
            {'continent': row[cols[4]], 'country': row[cols[7]], 'code':row[cols[6]], 'year': row[cols[9]], 'value': row[cols[23]]}
        )


    # Calcul de la moyenne et retour sous forme de liste de dict
    resultrr1 = compute_mean(rr1)

    context = {
        'sex_data': app_sexe,
        'regions_data': region_pays_dict,
        'app_dropdown': app_dropdown,
        'all_data': results1,
        'data_map': resultrr1,
        'qqqq': results55,
        'nodes': nodes,
        'links': links
    }

    return render(request, 'dashboard/home.html', context)

