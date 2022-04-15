from typing import List, Union

from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import pandas as pd
from .utils import list_files_dir, recup_mots_cle
from pandas_profiling import ProfileReport


def index(request: HttpRequest) -> HttpResponse:
    """
    BLA
    """
    return render(request, 'index.html')


def download_csv(request: HttpRequest) -> HttpResponse:
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
    if message := get_csv_message(request):
        messages.warning(request, message)
    return render(request, 'telecharger_csv.html')


def get_csv_message(request: HttpRequest) -> Union[str, None]:
    """
    BLA
    """
    if request.method != 'POST':
        return None
    if not (uploaded_file := request.FILES['document']).name.endswith('.csv'):
        return 'Le fichier n\'a pas été téléchargé. Merci de choisir un fichier au format csv'
    name = FileSystemStorage().save(uploaded_file.name, uploaded_file)
    df = pd.read_csv(f'media\\{name}', sep=';', engine='python', encoding='ansi')
    return f'Le fichier a été téléchargé avec succès. Il contient {df.shape[0]} ' \
           f'enregistrement(s) et {df.shape[1]} colonnes'


def download_pdf(request: HttpRequest) -> HttpResponse:
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
    if message := get_message(request, ".pdf"):
        messages.warning(request, message)
    return render(request, 'telecharger_pdf.html')


def get_message(request: HttpRequest, document_type:str) -> Union[str, None]:
    """
    BLA
    """
    if request.method != 'POST':
        return None
    if not (uploaded_file := request.FILES['document']).name.endswith(document_type):
        return f"Le fichier n\'a pas été téléchargé. Merci de choisir un fichier au format {document_type}"

    FileSystemStorage().save(uploaded_file.name, uploaded_file)
    return 'Le fichier a été téléchargé avec succès.'


def explorer(request: HttpRequest) -> HttpResponse:
    """
    1- display explorer page
    :param request:
    :return:
    """
    return render(request, 'explorer.html', {'list_files':  list_files_dir()})


def preparer(request: HttpRequest) -> HttpResponse:
    """
    BLA
    """
    return render(request, 'preparer.html', {'list_files': list_files_dir()})


def get_list_mots_cle(request: HttpRequest) -> HttpResponse:
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
    return resp(recup_mots_cle(f"media/{request.GET.get('file')}"))


def get_list_product(request: HttpRequest) -> HttpResponse:
    """
    BLA
    """
    df = pd.read_csv(f"media/{request.GET.get('file')}", sep=';', engine='python')
    return resp([name for name in df['product_name'] if request.GET.get('produit') in name])


def get_info_product(request: HttpRequest) -> JsonResponse:
    """
    Retourner les données relatives au produit choisi, aux produits à score nutritionnel
    équivalent et à l'ensemble des produits
    1- convertir le fichier CSV en dataframe
    2- supprimer les éléments nutritifs non concernés par le produit choisi
    3- supprimer la dimension count de la fonction describe
    :param request:
    :return: table des valeurs par élément nutritif
    """
    df = pd.read_csv(f"media/{request.GET.get('file')}", sep=';', engine='python', encoding='ansi')
    df_product = clean_product_csv(df, request.GET.get('produit'))
    products = df_product.style.set_properties(**{'text-align': 'right'})
    nutritive_elements = [products.index[idx] for idx, _ in enumerate(products.index)]
    categories = clean_category_csv(df, df_product, nutritive_elements)
    all_df = clean_all_csv(df, nutritive_elements)

    reponses = {'produit': products.to_html(),
                'categorie': categories.style.set_properties(**{'text-align': 'right'}).to_html(),
                'tous':  all_df.style.set_properties(**{'text-align': 'right'}).to_html()}
    return JsonResponse(reponses)


def clean_product_csv(df: pd.DataFrame, produit: str) -> pd.DataFrame:
    """
    BLA
    """

    cleaned_df = df[df.product_name == produit].drop(columns=['product_name'])\
        .dropna(axis=1, how='all').transpose()
    return cleaned_df.rename(columns={cleaned_df.columns[0]: 'valeur nutritive'}).round(decimals=4)


def clean_category_csv(df: pd.DataFrame,
                       df_product: pd.DataFrame,
                       nutritive_elements: List[str]
                       ) -> pd.DataFrame:
    """
    BLA
    """
    val = df_product.loc['nutrition-score-fr_100g']['valeur nutritive']
    clean_df = df.loc[(df['nutrition-score-fr_100g'] == val)].drop(columns=['product_name'])\
        .dropna(axis=1, how='all').filter(nutritive_elements, axis=1).describe().transpose()
    return clean_df.rename(columns={clean_df.columns[1]: 'valeur nutritive'})\
        .filter(['valeur nutritive'], axis=1)


def clean_all_csv(df: pd.DataFrame, nutritive_elements: List[str]) -> pd.DataFrame:
    """
    BLA
    """
    clean_df = df.drop(columns=['product_name']).dropna(axis=1, how='all')\
        .filter(nutritive_elements, axis=1).describe().transpose()
    return clean_df.rename(columns={clean_df.columns[1]: 'valeur nutritive'})\
        .filter(['valeur nutritive'], axis=1)


def get_list_colonnes(request: HttpRequest):
    """
    BLA
    """
    df = pd.read_csv(f"media/{request.GET.get('file')}", sep=';', engine='python', encoding='ansi')
    return resp(list(df.columns))


def get_overview(request: HttpRequest):
    """
    BLA
    """
    colonne = request.GET.get('colonne')
    filename = f"media/{request.GET.get('file')}"
    csv_file = pd.read_csv(filename, sep=';', engine='python', encoding='ansi')
    df = pd.DataFrame({'valeur': csv_file[colonne]})
    profile = ProfileReport(df, title=colonne, html={'style': {'full_width': True}})
    return JsonResponse({'overview': profile.to_html()})


def suppr_colonne(request: HttpRequest):
    """
    BLA
    """
    filename = f"media/{request.GET.get('file')}"
    csv_file = pd.read_csv(filename, sep=';', engine='python', encoding='ansi')
    csv_file.pop(request.GET.get('colonne'))
    csv_file.to_csv(filename, sep=';', encoding='ansi', index=False)
    return resp(csv_file.columns)


def resp(sequence: List[str]):
    """
    BLA
    """
    return HttpResponse(str(sequence))
