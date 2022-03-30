import os
import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import pandas as pd
import json
from elasticsearch import Elasticsearch, helpers
from .utils import get_plot, list_files_dir, cleanfile, recup_mots_cle
from pandas_profiling import ProfileReport
import re


def index (request):
    return render(request, 'index.html')

def telecharger_csv(request):
    """
    1- upload working file (csv only)
    2- storage of the file in the media directory
    3- read the uploaded file (fileUploaded) and calculate the number of records and columns
    Parameters
    ----------
    request
    Returns
    -------
    message with numbers of rows and columns
    """

    if request.method=='POST':
        uploaded_file=request.FILES['document']
        if uploaded_file.name.endswith('.csv'):
            name = FileSystemStorage().save(uploaded_file.name,uploaded_file)
            fileUploaded = 'media\\'+name
            my_file = pd.read_csv(fileUploaded, sep=';', engine='python', encoding='ansi')
            data = pd.DataFrame(data=my_file, index=None)
            rows = len(data.axes[0])
            columns = len(data.axes[1])
            messages.warning(request, 'Le fichier a été téléchargé avec succès. Il contient ' + str(rows) + ' enregistrement(s) et ' + str(columns) + ' colonnes')
        else:
            messages.warning(request, 'Le fichier n\'a pas été téléchargé. Merci de choisir un fichier au format csv')
    return render(request, 'telecharger_csv.html')

def telecharger_pdf(request):
    """
    1- upload working file (pdf only)
    2- storage of the file in the media directory
    Parameters
    ----------
    request
    Returns
    -------
    message with numbers of rows and columns
    """
    if request.method=='POST':
        uploaded_file=request.FILES['document']
        if uploaded_file.name.endswith('.pdf'):
            name = FileSystemStorage().save(uploaded_file.name,uploaded_file)
            messages.warning(request, 'Le fichier a été téléchargé avec succès.')
        else:
            messages.warning(request, 'Le fichier n\'a pas été téléchargé. Merci de choisir un fichier au format pdf')
    return render(request, 'telecharger_pdf.html')

def explorer(request):
    """
    1- display explorer page
    :param request:
    :return:
    """
    context={}
    list_files = list_files_dir()
    context['list_files'] = list_files
    return render(request, 'explorer.html', context)

def get_list_mots_cle(request):
    """
    1- get list of key words from product_name column
    Parameters:
    chosen file
    ----------
    request
    Returns
    key words list
    -------
    message with numbers of rows and columns
    """
    filename = 'media/'+request.GET.get('file')
    list_mots_cle = recup_mots_cle(filename)
    print(list_mots_cle)
    return HttpResponse(str(list_mots_cle))

def get_list_product(request):
    produit = request.GET.get('produit')
    filename = 'media/'+request.GET.get('file')
    csv_clean_file = pd.read_csv(filename, sep=';', engine='python')
    produits = []
    for index, row in csv_clean_file.iterrows():
        name = row['product_name']
        if produit in name:
            produits.append(name)
    return HttpResponse(str(produits))

def get_info_product(request):
    """
    Retourner les données relatives au produit choisi, aux produits à score nutritionnel équivalent et à l'ensemble des produits
    1- convertir le fichier CSV en dataframe
    2- supprimer les éléments nutritifs non concernés par le produit choisi
    3- supprimer la dimension count de la fonction describe
    :param request:
    :return: table des valeurs par élément nutritif
    """
    produit = request.GET.get('produit')
    filename = 'media/'+request.GET.get('file')
    csv_file = pd.read_csv(filename, sep=';', decimal='.', engine='python')
    csv_product = csv_file[csv_file.product_name == produit]
    csv_clean_file1 = csv_product.drop(columns=['product_name'])
    csv_clean_file2 = csv_clean_file1.dropna(axis=1, how='all')
    csv_clean_file3 = csv_clean_file2.transpose()
    csv_clean_file4 = csv_clean_file3.rename(columns={csv_clean_file3.columns[0]: 'valeur nutritive'})
    csv_clean_file5 = csv_clean_file4.round(decimals=4)
    val = csv_clean_file5.loc['nutrition-score-fr_100g']['valeur nutritive']
    csv_clean_file6 = csv_clean_file5.style.set_properties(**{'text-align': 'right'})

    elements_nutritifs=[]
    p=0
    for i in csv_clean_file6.index:
        elements_nutritifs.append(csv_clean_file6.index[p])
        p+=1

    csv_categorie = csv_file.loc[(csv_file['nutrition-score-fr_100g'] == val)]
    csv_clean_file7 = csv_categorie.drop(columns=['product_name'])
    csv_clean_file8 = csv_clean_file7.dropna(axis=1, how='all')
    csv_clean_file8 = csv_clean_file8.filter(elements_nutritifs, axis=1)
    csv_clean_file9 = csv_clean_file8.describe().transpose()
    csv_clean_file10 = csv_clean_file9.rename(columns={csv_clean_file9.columns[1]: 'valeur nutritive'})
    csv_clean_file11 = csv_clean_file10.filter(['valeur nutritive'], axis=1)
    csv_clean_file12 = csv_clean_file11.style.set_properties(**{'text-align': 'right'})

    csv_clean_file13 = csv_file.drop(columns=['product_name'])
    csv_clean_file14 = csv_clean_file13.dropna(axis=1, how='all')
    csv_clean_file14 = csv_clean_file14.filter(elements_nutritifs, axis=1)
    csv_clean_file15 = csv_clean_file14.describe().transpose()
    csv_clean_file16 = csv_clean_file15.rename(columns={csv_clean_file9.columns[1]: 'valeur nutritive'})
    csv_clean_file17 = csv_clean_file16.filter(['valeur nutritive'], axis=1)
    csv_clean_file18 = csv_clean_file17.style.set_properties(**{'text-align': 'right'})

    reponses={}
    reponses['produit'] = csv_clean_file6.to_html()
    reponses['categorie'] = csv_clean_file12.to_html()
    reponses['tous'] = csv_clean_file18.to_html()
    return JsonResponse(reponses)

def index_json():
    res = requests.get('http://localhost:9200')
    es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
    f = open('media/foodsClean.json')
    docket_content = f.read()
    # Send the data into es
    es.index(index='foods', ignore=400, doc_type='food', body=json.loads(docket_content))

def preparer(request):
    context={}
    list_files = list_files_dir()
    context['list_files'] = list_files
    return render(request, 'preparer.html', context)

def get_list_colonnes(request):
    file = request.GET.get('file')
    filename = 'media/'+file
    csv_file = pd.read_csv(filename, sep=';', engine='python', encoding='ansi')
    #df=csv_file.select_dtypes(include='number')
    colonnes = []
    for col_name in csv_file.columns:
        colonnes.append(col_name)
    return HttpResponse(str(colonnes))

def get_overview(request):
    context = {}
    file = request.GET.get('file')
    colonne = request.GET.get('colonne')
    filename = 'media/' + file
    csv_file = pd.read_csv(filename, sep=';', engine='python', encoding='ansi')
    df = pd.DataFrame({'valeur': csv_file[colonne]})

    profile = ProfileReport(df, title=colonne, html={'style': {'full_width': True}})

    #profile = Profile Report(df, minimal=True)
    rapport = profile.to_html()
    context['overview']=rapport
    # type_colonne =csv_file[colonne].dtype
    # if(type_colonne!='object'):
    #     #Resume
    #     value_counts = pd.DataFrame({'valeur': csv_file[colonne].describe().transpose()})
    #     # df_centered = df.apply(lambda x: (x-x.mean())/x.std())
    #     context['value_counts'] = rapport #value_counts.to_html()
    #     #Chart
    #     chart = get_plot(df, colonne)
    #     context['chart'] = chart
    # else:
    #     message = "La colonne ne correspondant pas à une variable continue."
    #     context['message'] = message

    return JsonResponse(context)

def get_values_colonne(request):
    context = {}
    file = request.GET.get('file')
    colonne = request.GET.get('colonne')
    filename = 'media/' + file
    csv_file = pd.read_csv(filename, sep=';', engine='python', encoding='ansi')
    df = pd.DataFrame({'valeur': csv_file[colonne]})
    values = pd.unique(df['valeur'])
    values_all=[]
    for val in values:
        if (len(str(val))>0):
            values_row = re.findall(r'\[.*?\]', str(val))
            # values_row = [sub.replace('[', '') for sub in values_row]
            # values_row = [sub.replace(']', '') for sub in values_row]
            values_all.append(values_row)
    json_str = json.dumps(values_all)
    print(json_str)
    #context['values_colonne'] = str(values_all)
    return JsonResponse(json_str, safe=False)

def suppr_colonne(request):
    context = {}
    file = request.GET.get('file')
    colonne = request.GET.get('colonne')
    filename = 'media/' + file
    csv_file = pd.read_csv(filename, sep=';', engine='python', encoding='ansi')
    csv_file.pop(colonne)
    os.remove(filename)
    csv_file.to_csv(filename, sep=';', encoding='ansi', index=True)
    #df = pd.read_csv(filename, sep=';', engine='python', encoding='ansi')
    colonnes = []
    for col_name in csv_file.columns:
        colonnes.append(col_name)
    return HttpResponse(str(colonnes))
