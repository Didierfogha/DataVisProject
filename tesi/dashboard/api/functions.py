import re
import pandas as pd

def compare_expectancies(label1, label2):

    # Extraire l'âge à partir de la deuxième string
    match = re.search(r'age\s+(\d+\s*\(years\))', label2)
    if match:
        suffix = match.group(1)
        return f"{label1} vs {suffix}"
    else:
        return f"{label1} vs [unknown age]"

def short_compare(label1, label2):
    # Extraire "birth (years)" depuis label1
    part1 = re.search(r'(birth\s*\(years\))', label1, re.IGNORECASE)
    short1 = part1.group(1) if part1 else label1

    # Extraire "60 (years)" ou autre depuis label2
    part2 = re.search(r'age\s+(\d+\s*\(years\))', label2, re.IGNORECASE)
    short2 = part2.group(1) if part2 else label2

    return f"{short1} vs {short2}"

def filter_dataframe(df, filters):
    """
    Filtre un DataFrame selon des valeurs spécifiées.

    :param df: pandas.DataFrame original à filtrer
    :param filters: dict des filtres sous la forme {"colonne": valeur}
                    - Si valeur est None ou "", elle est ignorée
                    - Si valeur est une liste, filtre sur plusieurs valeurs (isin)
    :return: DataFrame filtré
    """
    df_filtered = df.copy()
    for column, value in filters.items():
        if value is None or value == "":
            continue
        if isinstance(value, list):
            df_filtered = df_filtered[df_filtered[column].isin(value)]
        else:
            df_filtered = df_filtered[df_filtered[column] == value]
    return df_filtered