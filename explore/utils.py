import io

import matplotlib.pyplot as plt
import seaborn as sns
import base64
import os
import json
import pandas as pd

def get_graph():
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(x, nom_colonne):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10,3))
    plt.title(nom_colonne)
    #plt.plot(x)
    plt.hist(x, bins=100)
    plt.gca().set(title=nom_colonne, ylabel='Frequency');
    plt.xticks(rotation=45)
    # plt.xlabel('axe_absisses')
    plt.tight_layout()
    graph = get_graph()
    return graph

def list_files_dir():
    path = 'media/'
    list_files=[]
    files = os.listdir(path)
    for f in files:
        if f.endswith('.csv'):
            list_files.append(f)
    return list_files

# Suppression des colonnes avec valeurs = null, suppression des colonnes sans intérêt pour l'analyse et création du fichier JSON
def cleanfile():
    #liste des variables utiles
    header = ['product_name','energy_100g','energy-from-fat_100g','fat_100g','saturated-fat_100g','butyric-acid_100g','caproic-acid_100g','caprylic-acid_100g','capric-acid_100g','lauric-acid_100g','myristic-acid_100g','palmitic-acid_100g','stearic-acid_100g','arachidic-acid_100g','behenic-acid_100g','lignoceric-acid_100g','cerotic-acid_100g','montanic-acid_100g','melissic-acid_100g','monounsaturated-fat_100g','polyunsaturated-fat_100g','omega-3-fat_100g','alpha-linolenic-acid_100g','eicosapentaenoic-acid_100g','docosahexaenoic-acid_100g','omega-6-fat_100g','linoleic-acid_100g','arachidonic-acid_100g','gamma-linolenic-acid_100g','dihomo-gamma-linolenic-acid_100g','omega-9-fat_100g','oleic-acid_100g','elaidic-acid_100g','gondoic-acid_100g','mead-acid_100g','erucic-acid_100g','nervonic-acid_100g','trans-fat_100g','cholesterol_100g','carbohydrates_100g','sugars_100g','sucrose_100g','glucose_100g','fructose_100g','lactose_100g','maltose_100g','maltodextrins_100g','starch_100g','polyols_100g','fiber_100g','proteins_100g','casein_100g','serum-proteins_100g','nucleotides_100g','salt_100g','sodium_100g','alcohol_100g','vitamin-a_100g','beta-carotene_100g','vitamin-d_100g','vitamin-e_100g','vitamin-k_100g','vitamin-c_100g','vitamin-b1_100g','vitamin-b2_100g','vitamin-pp_100g','vitamin-b6_100g','vitamin-b9_100g','folates_100g','vitamin-b12_100g','biotin_100g','pantothenic-acid_100g','silica_100g','bicarbonate_100g','potassium_100g','chloride_100g','calcium_100g','phosphorus_100g','iron_100g','magnesium_100g','zinc_100g','copper_100g','manganese_100g','fluoride_100g','selenium_100g','chromium_100g','molybdenum_100g','iodine_100g','caffeine_100g','taurine_100g','ph_100g','fruits-vegetables-nuts_100g','collagen-meat-protein-ratio_100g','cocoa_100g','chlorophyl_100g','carbon-footprint_100g','nutrition-score-fr_100g','glycemic-index_100g','water-hardness_100g']

    #Récupération du fichier JSON avant nettoyage des données
    with open("media/foods.json") as json_file:
        data_json = json.load(json_file)
        length = len(data_json)
        #Création du fichier JSON destiné à contenir les données nettoyées
        open('media/foodsClean.json','w')
        list_all_obj = []
        for i in range(length):
            list_obj = {}
            item = data_json[i]
            for key in item:
                #if (item[key]!=None and key in header):
                if (key in header):
                    list_obj[key] = item[key]
            list_all_obj.append(list_obj)
        with open("media/foodsClean.json", "a") as file:
            json.dump(list_all_obj, file)
        file.close()

# def readfile(filename):
#     global rows, columns, mots_cle
#     context={}
#     my_file =pd.read_csv(filename, sep=';', engine='python', encoding='ansi')
#
#     #Récupération des données dans un Dataframe et création du fichier JSON correspondant
#     data = pd.DataFrame(data=my_file, index=None)
#     data.to_json(path_or_buf='media/foods.json', orient='records')
#
#     #Calculer le nombre d'enregistrements et de colonnes
#     rows = len(data.axes[0])
#     columns = len(data.axes[1])
#
#     cleanfile()
#     #convert_json_to_csv()

    #Récupérer la liste des mots clé contenus dans la variable 'product_name'
def recup_mots_cle(filename):
    csv_clean_file = pd.read_csv(filename, sep=';', engine='python', encoding='utf-8')
    mots_cle =[]
    for index, row in csv_clean_file.iterrows():
        name = row['product_name']
        if(isinstance(name,str)):
            elem_name = name.split()
            for mot in elem_name:
                if(len(mot)>2):
                    mots_cle.append(mot)

    #supprimer les doublons dans la liste des mots clé
    mots_cle = list(set(mots_cle))
    return mots_cle

def convert_json_to_csv(filename):
    # Récupération des données du fichier JSON et création du dataframe correspondant
    my_json_file = pd.read_json('media/'+filename)
    data = pd.DataFrame(data=my_json_file, index=None)
    # conversion des données dans un fichier CSV
    data.to_csv('media/'+filename, index= False, sep=';', encoding ='ansi')
