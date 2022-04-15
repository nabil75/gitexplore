import io
from typing import List

import matplotlib.pyplot as plt
import base64
import os
import json
import pandas as pd

HEADERS = ['product_name', 'energy_100g', 'energy-from-fat_100g', 'fat_100g', 'saturated-fat_100g',
           'butyric-acid_100g', 'caproic-acid_100g', 'caprylic-acid_100g', 'capric-acid_100g',
           'lauric-acid_100g', 'myristic-acid_100g', 'palmitic-acid_100g', 'stearic-acid_100g',
           'arachidic-acid_100g', 'behenic-acid_100g', 'lignoceric-acid_100g', 'cerotic-acid_100g',
           'montanic-acid_100g', 'melissic-acid_100g', 'monounsaturated-fat_100g',
           'polyunsaturated-fat_100g', 'omega-3-fat_100g', 'alpha-linolenic-acid_100g',
           'eicosapentaenoic-acid_100g', 'docosahexaenoic-acid_100g', 'omega-6-fat_100g',
           'linoleic-acid_100g', 'arachidonic-acid_100g', 'gamma-linolenic-acid_100g',
           'dihomo-gamma-linolenic-acid_100g', 'omega-9-fat_100g', 'oleic-acid_100g',
           'elaidic-acid_100g', 'gondoic-acid_100g', 'mead-acid_100g', 'erucic-acid_100g',
           'nervonic-acid_100g', 'trans-fat_100g', 'cholesterol_100g', 'carbohydrates_100g',
           'sugars_100g', 'sucrose_100g', 'glucose_100g', 'fructose_100g', 'lactose_100g',
           'maltose_100g', 'maltodextrins_100g', 'starch_100g', 'polyols_100g', 'fiber_100g',
           'proteins_100g', 'casein_100g', 'serum-proteins_100g', 'nucleotides_100g',
           'salt_100g', 'sodium_100g', 'alcohol_100g', 'vitamin-a_100g', 'beta-carotene_100g',
           'vitamin-d_100g', 'vitamin-e_100g', 'vitamin-k_100g', 'vitamin-c_100g',
           'vitamin-b1_100g', 'vitamin-b2_100g', 'vitamin-pp_100g', 'vitamin-b6_100g',
           'vitamin-b9_100g', 'folates_100g', 'vitamin-b12_100g', 'biotin_100g',
           'pantothenic-acid_100g', 'silica_100g', 'bicarbonate_100g', 'potassium_100g',
           'chloride_100g', 'calcium_100g', 'phosphorus_100g', 'iron_100g', 'magnesium_100g',
           'zinc_100g', 'copper_100g', 'manganese_100g', 'fluoride_100g', 'selenium_100g',
           'chromium_100g', 'molybdenum_100g', 'iodine_100g', 'caffeine_100g', 'taurine_100g',
           'ph_100g', 'fruits-vegetables-nuts_100g', 'collagen-meat-protein-ratio_100g',
           'cocoa_100g', 'chlorophyl_100g', 'carbon-footprint_100g', 'nutrition-score-fr_100g',
           'glycemic-index_100g', 'water-hardness_100g']


def get_graph():
    """
    BLA
    """
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png).decode('utf-8')
    buffer.close()
    return graph


def get_plot(x, title: str):
    """
    BLA
    """
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 3))
    plt.title(title)
    plt.hist(x, bins=100)
    plt.gca().set(title=title, ylabel='Frequency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return get_graph()


def list_files_dir() -> List[str]:
    """
    BLA
    """
    return [f for f in os.listdir('media/') if f.endswith('.csv')]


def cleanfile():
    """
    Suppression des colonnes avec valeurs = null, suppression des colonnes sans intérêt
     pour l'analyse et création du fichier JSON.
    """
    with open("media/foods.json") as json_file:
        data_json = json.load(json_file)
        with open("media/foodsClean.json", "a") as file:
            json.dump([{key: val[key] for key in val if key in HEADERS} for val in data_json], file)
        file.close()


def recup_mots_cle(filename) -> List[str]:
    """
    BLA
    """
    products = pd.read_csv(filename, sep=';', engine='python', encoding='utf-8')['product_name']
    mots_cle = []
    for product in [product for product in products if isinstance(product, str)]:
        mots_cle.extend(mot for mot in product.split() if len(mot) > 2)
    return list(set(mots_cle))


def convert_json_to_csv(filename: str) -> None:
    """
    Récupération des données du fichier JSON et création du dataframe correspondant.
    Conversion des données dans un fichier CSV
    """
    data = pd.DataFrame(data=pd.read_json(f'media/{filename}'), index=None)
    data.to_csv(f'media/{filename}', index=False, sep=';', encoding='ansi')
