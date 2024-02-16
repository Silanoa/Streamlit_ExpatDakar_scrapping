import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get, exceptions
import base64
import numpy as np
import os
import time
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

def main():
    # Configuration de la page Streamlit
    st.set_page_config(page_title="Application de Scraping", page_icon=":bar_chart:", layout="wide")

    # Fonction pour convertir DataFrame en CSV
    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    # Fonction pour charger et afficher les données
    def load(dataframe, title, key, key1):
        st.markdown("""
            <style>
            div.stButton {text-align:center; margin-top: 1rem;}
            .dataframe {font-size: 16px; text-align: left;}
            .title {
                color: #3498db;
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)
        st.write(f"<h2 class='title'>{title}</h2>", unsafe_allow_html=True)
        st.write(f"Dimensions des données : {dataframe.shape[0]} lignes et {dataframe.shape[1]} colonnes.")
        st.dataframe(dataframe, height=500)
        csv = convert_df(dataframe)
        st.download_button(
            label="Télécharger les données au format CSV",
            data=csv,
            file_name='Donnees.csv',
            mime='text/csv',
            key=key,
            help="Cliquez pour télécharger les données"
        )

    st.markdown("""
        <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f0f0f0;
        }
        h2 {
            color: #3498db;
            text-align: center;
        }
        
        .sidebar .sidebar-content {
            background-color: #2c3e50;
            color: white;
        }
        .sidebar .stSelectbox {
            background-color: #3498db;
            color: white;
        }
        .dataframe {
            background-color: #ffffff;
            border: 1px solid #d3d3d3;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .title {
            color: #3498db;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    df = pd.read_csv("expat_telephones.csv")
    stats_ordinateur = pd.read_csv("stats_ordinateur.csv")
    stats_phone = pd.read_csv("stats_phone.csv")
    stats_tvmacro = pd.read_csv("stats_tv_home.csv")

    def extraire_donnees_ordi(nb_pages):
        df = pd.DataFrame()
        barre_progression = st.progress(0)

        for p in range(1, nb_pages + 1):
            url = f'https://www.expat-dakar.com/ordinateurs?page={p}'
            retries = 5
            for _ in range(retries):
                try:
                    resp = get(url)
                    resp.raise_for_status()
                    break
                except exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        #st.warning(f"Erreur 429: Trop de requêtes. Réessai dans 30 secondes...")
                        time.sleep(30)
                    else:
                        pass
                        break
                except exceptions.RequestException as e:
                    pass
                    break
            try:
                resp = get(url)
                resp.raise_for_status()
            except exceptions.RequestException as e:
                pass
                continue
            soup = bs(resp.text, 'html.parser')
            links_a = soup.find_all('a', class_='listing-card__inner')
            links = [link['href'] for link in links_a]

            data = []
            for link in links:
                res = get(link)
                soup = bs(res.text, 'html.parser')
                try:
                    adresse = soup.find('span', class_='listing-item__address-location').text.strip()
                    region = soup.find('span', class_='listing-item__address-region').text.strip()
                    prix = soup.find('span', class_='listing-card__price__value 1').text.strip().replace('\u202f', '').replace('F Cfa', '')
                    description = soup.find('div', class_='listing-item__description').text.strip().replace('\nV', '').replace('\nv', '')
                    try:
                        inf = soup.find_all('dd', class_='listing-item__properties__description')
                        etat = inf[0].text.strip()
                    except:
                        etat = np.nan
                    try:
                        marque = inf[1].text.strip()
                    except:
                        marque = np.nan
                    try:
                        images = soup.find_all("img", class_="gallery__image__resource")
                        image_links = []
                        for i in range(len(images)):
                            image = images[i]
                            image_link = image["src"]
                            if "listing-thumb" in image_link:
                                image_links.append(image_link)
                    except :
                        image_links = np.nan

                    obj = {
                        'etat': etat,
                        'marque': marque,
                        'adresse': adresse,
                        'region': region,
                        'prix': prix,
                        'description': description,
                        'image_links': image_links
                    }
                    data.append(obj)
                except:
                    pass

            DF = pd.DataFrame(data)
            df = pd.concat([df, DF], axis=0).reset_index(drop=True)
            barre_progression.progress(int((p / nb_pages) * 100))
            
        st.success("Le scraping est terminé avec succès !")
        return df

    def extraire_donnees_phone(nb_pages):
        df = pd.DataFrame()
        barre_progression = st.progress(0)

        for p in range(1, nb_pages+1):
            url = f'https://www.expat-dakar.com/telephones?page={p}'
            retries = 5
            for _ in range(retries):
                try:
                    resp = get(url)
                    resp.raise_for_status()
                    break
                except exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        #st.warning(f"Erreur 429: Trop de requêtes. Réessai dans 30 secondes...")
                        time.sleep(30)
                    else:
                        pass
                        break
                except exceptions.RequestException as e:
                    pass
                    break
            try:
                resp = get(url)
                resp.raise_for_status()
            except exceptions.RequestException as e:
                pass
                continue
            soup = bs(resp.text, 'html.parser')
            links_a = soup.find_all('a', class_='listing-card__inner')
            links = [link['href'] for link in links_a]
            data = []

            for link in links:
                res = get(link)
                Soup = bs(res.text, 'html.parser')

                try:
                    adresse = Soup.find('span', class_='listing-item__address-location').text.strip()
                    region = Soup.find('span', class_='listing-item__address-region').text.strip()
                    prix = Soup.find('span', class_='listing-card__price__value 1').text.strip().replace('\u202f', '').replace('F Cfa', '')
                    description = Soup.find('div', class_='listing-item__description').text.strip().replace('\nV', '').replace('\nv', '')

                    try:
                        inf = Soup.find_all('dd', class_='listing-item__properties__description')
                        etat = inf[0].text.strip() if inf and len(inf) > 0 else np.nan
                        marque = inf[1].text.strip() if inf and len(inf) > 1 else np.nan

                        image_links = []
                        images = Soup.find_all("img", class_="gallery__image__resource")
                        for i in range(5):
                            if i < len(images):
                                image = images[i]
                                image_link = image["src"]
                                image_links.append(image_link)
                            else:
                                image_links.append(np.nan)
                    except:
                        etat = marque = np.nan
                        image_links = np.nan

                    obj = {
                        'etat': etat,
                        'marque': marque,
                        'adresse': adresse,
                        'region': region,
                        'prix': prix,
                        'description': description,
                        'image_links': image_links
                    }
                    data.append(obj)
                except:
                    pass

            DF = pd.DataFrame(data)
            df = pd.concat([df, DF], axis=0, ignore_index=True)
            barre_progression.progress(int((p / nb_pages) * 100))
            
        st.success("Le scraping est terminé avec succès !")
        return df

    def extraire_donnees_tv(nb_pages):
        df = pd.DataFrame()
        barre_progression = st.progress(0)

        for p in range(1, nb_pages+1):
            url = f'https://www.expat-dakar.com/tv-home-cinema?page={p}'
            retries = 5
            for _ in range(retries):
                try:
                    resp = get(url)
                    resp.raise_for_status()
                    break
                except exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        #st.warning(f"Erreur 429: Trop de requêtes. Réessai dans 30 secondes...")
                        time.sleep(30)
                    else:
                        pass
                        break
                except exceptions.RequestException as e:
                    pass
                    break
            try:
                resp = get(url)
                resp.raise_for_status()
            except exceptions.RequestException as e:
                pass
                continue
            soup = bs(resp.text, 'html.parser')
            links_a = soup.find_all('a', class_='listing-card__inner')
            links = [link['href'] for link in links_a]
            data = []

            for link in links:
                res = get(link)
                Soup = bs(res.text, 'html.parser')

                try:
                    adresse = Soup.find('span', class_='listing-item__address-location').text.strip()
                    region = Soup.find('span', class_='listing-item__address-region').text.strip()
                    prix = Soup.find('span', class_='listing-card__price__value 1').text.strip().replace('\u202f', '').replace('F Cfa', '')
                    description = Soup.find('div', class_='listing-item__description').text.strip().replace('\nV', '').replace('\nv', '')

                    try:
                        inf = Soup.find_all('dd', class_='listing-item__properties__description')
                        etat = inf[0].text.strip() if inf and len(inf) > 0 else np.nan
                        marque = inf[1].text.strip() if inf and len(inf) > 1 else np.nan

                        image_links = []
                        images = Soup.find_all("img", class_="gallery__image__resource")
                        for i in range(5):
                            if i < len(images):
                                image = images[i]
                                image_link = image["src"]
                                image_links.append(image_link)
                            else:
                                image_links.append(np.nan)
                    except:
                        etat = marque = np.nan
                        image_links = np.nan

                    obj = {
                        'etat': etat,
                        'marque': marque,
                        'adresse': adresse,
                        'region': region,
                        'prix': prix,
                        'description': description,
                        'image_links': image_links
                    }
                    data.append(obj)
                except:
                    pass

            DF = pd.DataFrame(data)
            df = pd.concat([df, DF], axis=0, ignore_index=True)
            barre_progression.progress(int((p / nb_pages) * 100))
        st.success("Le scraping est terminé avec succès !")
        return df

    def afficher_statistiques(data):
        data = data.drop('Unnamed: 0', axis=1)
        st.write("## Statistiques sur les données scrappées")
        st.write("### Description des données")
        st.write(data.describe())
        
        st.write("### Tableau de bord des Statistiques")

        # Créer une mise en page à deux colonnes
        col1, col2 = st.columns(2)

        # Tracer l'histogramme des prix
        col1.write("### Histogramme des prix")
        fig_hist = px.histogram(data, x='prix', nbins=20, title='Prix')
        col1.plotly_chart(fig_hist)

        # Nombre d'annonces par état
        col1.write("### Nombre d'annonces par état")
        fig_condition = px.bar(data.groupby('etat').size().reset_index(name='count'), x='count', y='etat', orientation='h',
                            color='etat', color_discrete_sequence=px.colors.qualitative.Dark2)
        col1.plotly_chart(fig_condition)

        # Nombre d'annonces par région
        col2.write("### Nombre d'annonces par région")
        fig_region = px.bar(data.groupby('region').size().reset_index(name='count'), x='count', y='region', orientation='h',
                            color='region', color_discrete_sequence=px.colors.qualitative.Dark2)
        col2.plotly_chart(fig_region)

        # Nombre d'annonces par marque
        col2.write("### Nombre d'annonces par marque")
        fig_brand = px.bar(data.groupby('marque').size().reset_index(name='count'), x='count', y='marque', orientation='h',
                        color='marque', color_discrete_sequence=px.colors.qualitative.Dark2)
        col2.plotly_chart(fig_brand)

        # Nombre d'annonces par marque et état
        st.write("### Nombre d'annonces par marque et état")
        fig_brand_condition = px.bar(data.groupby(['marque', 'etat']).size().reset_index(name='count'), x='marque', y='count',
                                    color='etat', barmode='stack', color_discrete_sequence=px.colors.qualitative.Dark2)
        st.plotly_chart(fig_brand_condition)

        # Nuage de points du prix par état
        st.write("### Relation entre le prix et l'état")
        fig_scatter = px.scatter(data, x='prix', y='etat', color='etat', opacity=0.5, title='Prix vs. Condition')
        st.plotly_chart(fig_scatter)

    # Application Streamlit
    st.markdown("<h2 class='title'>APPLICATION DE SCRAPPING DE DONNÉES DEPUIS LE SITE EXPAT-DAKAR</h2>", unsafe_allow_html=True)
    st.markdown("""
        * **Librairies Python :** base64, pandas, streamlit, requests, bs4
        * **Source de données :** [Expat-Dakar](https://www.expat-dakar.com/).
    """)


    st.sidebar.success("Choisissez une opération")
    nb_pages_a_scrapper = st.sidebar.selectbox("Sélectionnez le nombre de pages à scraper :", list(range(1, 447)))
    options = ["Scrapper avec BeautifulSoup", "Télécharger les données scrappées avec Web sCrapper", "Afficher les statistiques","Remplir le formulaire"]
    selected_option = st.sidebar.selectbox("Sélectionnez une option",
                                        options,
                                        index=None,
                                        placeholder="Sélectionner votre option",)
    st.sidebar.write("Option sélectionnée :", selected_option)

    # Charger les données
    if selected_option == "Scrapper avec BeautifulSoup":
        st.markdown("""
            <style>
            div.stButton {text-align:center; margin-top: 1rem;}
            .dataframe {font-size: 16px; text-align: left;}
            </style>
        """, unsafe_allow_html=True)

        selected_category = st.radio("Choisir la catégorie à scraper :", ['Téléphones', 'Ordinateurs', 'Tv Home-Cinema'])

        if st.button('Scrapper les données'):
            if selected_category == 'Ordinateurs':
                donnees_scrappees = extraire_donnees_ordi(nb_pages_a_scrapper)
                #st.write('Données Scrappées des ordinateurs :')
                #st.write(donnees_scrappees)  
                #placeholder = st.empty()
                load(donnees_scrappees, 'Données Scrappées des ordinateurs', '1', '101')
                #placeholder.dataframe(donnees_scrappees, height=500)

            elif selected_category == 'Téléphones':
                donnees_scrappees = extraire_donnees_phone(nb_pages_a_scrapper)
                #st.write('Données Scrappées des téléphones :')
                #st.write(donnees_scrappees)  
                #placeholder = st.empty()
                load(donnees_scrappees, 'Données Scrappées des téléphones', '1', '101')
                #placeholder.dataframe(donnees_scrappees, height=500)

            elif selected_category == 'Tv Home-Cinema':
                donnees_scrappees = extraire_donnees_tv(nb_pages_a_scrapper)
                #st.write('Données Scrappées des tv-home :')
                #st.write(donnees_scrappees)
                #placeholder = st.empty()
                load(donnees_scrappees, 'Données Scrappées des tv-home', '1', '101')
                #placeholder.dataframe(donnees_scrappees, height=500)

    elif selected_option == "Télécharger les données scrappées avec Web sCrapper":
        st.markdown("""
            <style>
            div.stButton {text-align:center; margin-top: 1rem;}
            .dataframe {font-size: 16px; text-align: left;}
            </style>
        """, unsafe_allow_html=True)
        st.write("Choisir la catégorie de données à télécharger")
        
        selected_category_to_download = st.radio("Catégorie :", ['Ordinateurs', 'Téléphones', 'Tv Home-Cinema'])
        if selected_category_to_download == 'Ordinateurs':
            csv_file_to_download = 'expat_ordinateurs.csv'
        elif selected_category_to_download == 'Téléphones':
            csv_file_to_download = 'expat_telephones.csv'
        elif selected_category_to_download == 'Tv Home-Cinema':
            csv_file_to_download = 'expat_tv_home_cinemas.csv'
        if st.button("Vérification"):
            csv_file_path = os.path.join(os.getcwd(), csv_file_to_download)
            st.download_button(
                label=f"Télécharger les données {selected_category_to_download} au format CSV",
                data=open(csv_file_path, 'rb'),
                file_name=csv_file_to_download,
                mime='text/csv',
                key='download-csv',
                help="Cliquez pour télécharger les données"
            )
    elif  selected_option == "Afficher les statistiques":
        selected_category = st.radio("Choisissez une catégorie :", ['Téléphones', 'Ordinateurs', 'Tv Home-Cinema'])

        if st.button('Afficher les statistiques'):
            if selected_category == 'Ordinateurs':
                afficher_statistiques(stats_ordinateur)
            elif selected_category == 'Téléphones':
                afficher_statistiques(stats_phone)
            elif selected_category == 'Tv Home-Cinema':
                afficher_statistiques(stats_tvmacro)
    elif selected_option == "Remplir le formulaire" :
        st.components.v1.iframe(src='https://ee.kobotoolbox.org/i/LOxynrgZ',
                                width=800,
                                height=800)
        
if __name__ == "__main__":
    main()