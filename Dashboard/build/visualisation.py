from pathlib import Path
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import sys
import tkintermapview
import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from shapely.geometry import Point


class Visualisation_des_accidents:
    def __init__(self, file_path):
        self.file_path = Path(file_path).resolve()
        if not self.file_path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {self.file_path}")
        print(f"Chemin du fichier Excel : {self.file_path}")
        self.colors = [
        '#1f77b4', '#5da5da', '#2ca02c', '#d62728', '#9467bd', '#ffbb78',
        '#e377c2', 'orange', '#FF6500', '#6895D2', '#FF3C00', '#F9FFA5'
    ]

    def plot_accidents_par_categorie(self):
        df = pd.read_excel(self.file_path, engine="openpyxl", sheet_name="Accident_corporels")
        df = df[df['CATEGORIE'] != 'TOTAL']

        categories = df["CATEGORIE"].tolist()
        values_outer = (df["MORTELS"] + df["N. MORTELS"]).tolist()
        values_inner = df[["MORTELS", "N. MORTELS"]].values.flatten().tolist()

        outer_colors = ['#FF6500', '#6895D2']
        inner_colors = ['#FF3C00', '#F9FFA5', '#4682B4', '#ADD8E6']

        fig, ax = plt.subplots(figsize=(5, 5))
        fig.patch.set_facecolor('#231E6D')
        ax.set_facecolor('#231E6D')

        # pie exterieure
        wedges_outer, texts_outer = ax.pie(
            values_outer, radius=1, colors=outer_colors, startangle=90,
            wedgeprops=dict(width=0.3, edgecolor='w')
        )

        # Pie interieure
        wedges_inner, texts_inner, autotexts_inner = ax.pie(
            values_inner, radius=0.7, colors=inner_colors, startangle=90,
            wedgeprops=dict(width=0.3, edgecolor='w'), autopct='%1.1f%%',
            textprops={'color': 'black'}
        )

        #legendre
        legend_labels = (
            [f'{cat} (Total)' for cat in categories] +  # Outer labels
            [f'{cat} - Mortels' for cat in categories] +  # Inner labels (Mortels)
            [f'{cat} - Non Mortels' for cat in categories]  # Inner labels (Non Mortels)
        )
        legend_wedges = wedges_outer + wedges_inner
        legend = plt.legend(
            legend_wedges, legend_labels,
            title="Catégories et Sous-Catégories",
            loc="upper center", bbox_to_anchor=(0.5, 0.5),
            facecolor='#384780', edgecolor='white', labelcolor='white', title_fontsize=10
        )
        legend.set_visible(False)
        #effet hover pour afficher la legende
        def on_hover(event):
            if event.inaxes == ax:
                legend.set_visible(True)
            else:
                legend.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)

        plt.title("Accidents par Catégorie et Sous-Catégorie", fontsize=10, color='white', loc='center', pad=1)
        plt.tight_layout()
        return fig

    def plot_evolution_des_accidents(self):
        df = pd.read_excel(self.file_path, engine="openpyxl", sheet_name="Evolution_accident_2008_2020")
        df_melted = df.melt(id_vars=["Unnamed: 0"], var_name="Year", value_name="Count")
        df_melted.rename(columns={"Unnamed: 0": "Category"}, inplace=True)
        df_melted['Year'] = pd.to_datetime(df_melted['Year'], format='%Y', errors='coerce')
        df_melted.dropna(inplace=True)
        pivot_df = df_melted.pivot(index='Year', columns='Category', values='Count').fillna(0)

        fig = plt.figure(figsize=(6, 5))
        plt.gcf().set_facecolor('#231E6D')
        plt.gca().set_facecolor('#231E6D')

        for column in pivot_df.columns:
            plt.fill_between(pivot_df.index, pivot_df[column], alpha=0.5, label=column)
            plt.plot(pivot_df.index, pivot_df[column], linewidth=2, label=f"Ligne {column}")

        plt.title('Evolution des Accidents de 2008 à 2020', fontsize=8, color='white')
        plt.xlabel('Année', fontsize=8, color='white')
        plt.ylabel('Nombre', fontsize=8, color='white')
        plt.tick_params(colors='white')
        plt.grid(color='white', linestyle='--', linewidth=0.3)
        plt.tight_layout()

        plt.legend(title='Catégories', facecolor='#384780', edgecolor='white', labelcolor='white', title_fontsize=12)
        legend = plt.legend(
            title='Catégories',
            facecolor='#384780',
            edgecolor='white',
            labelcolor='white',
            title_fontsize=12
        )
        legend.set_visible(False)

        def on_hover(event):
            if event.inaxes == plt.gca():
                legend.set_visible(True)
            else:
                legend.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)
        
        return fig 
        
    def plot_accidents_par_jours(self):
        df = pd.read_excel(self.file_path, engine="openpyxl", sheet_name="ACCID_VICTIME_PAR_JOUR")
        df = df.drop(columns=["ACCID MORT", "ACCID N.MORT", "TUES", "BLES LEGER", "BLES GRAV"])
        df.set_index('JOUR DE SEMAINE', inplace=True)

        plt.figure(figsize=(9, 4))
        plt.gcf().set_facecolor('#231E6D')
        plt.gca().set_facecolor('#231E6D')

        for column in df.columns:
            plt.plot(df.index, df[column], marker='o', label=column, color='#ff7f0e')

        plt.title('Répartition des Accidents par Jour de la Semaine', fontsize=10, color='white')
        plt.xlabel('Jour de la Semaine', fontsize=8, color='white')
        plt.ylabel('Nombre de Victimes', fontsize=8, color='white')
        plt.tick_params(colors='white')
        plt.legend(title='Types de Victimes', facecolor='#384780', edgecolor='white', labelcolor='white', title_fontsize=12)
        plt.grid(color='white', linestyle='--', linewidth=0.5)
        plt.xticks(rotation=45, color='white')
        plt.yticks(color='white')
        plt.tight_layout()
        return plt.gcf()
        

    def plot_victimes_par_categorie_usagers(self):
        
        df = pd.read_excel(self.file_path, engine="openpyxl", sheet_name="VICTIME_PAR_CATEGORIE_DUSAGERS ")
        df = df.set_index("CATEGORIE DUSAGERS")

        
        fig = plt.figure(figsize=(6, 6))
        plt.gcf().set_facecolor('#231E6D')
        plt.gca().set_facecolor('#231E6D')

        # Paramètres des segments du graphique
        explode = [0.0, 0, 0.1, 0.0, 0.1, 0.0, 0.0, 0.1]
        wedges, texts, autotexts = plt.pie(
            df['VICTIMES'], 
            explode=explode, 
            autopct='%1.1f%%', 
            colors=self.colors[:len(df)], 
            textprops={'color': 'white'}  # Texte des étiquettes en blanc
        )

        # Ajouter un titre
        plt.title("Victimes par categorie d'usagers", fontsize=12, color='white', pad=0, fontweight='bold',)
        # Ajouter une légende
        legend = plt.legend(
            wedges,  # Associe chaque wedge à une étiquette
            df.index,  # Index des catégories
            title="Catégories d'Usagers",
            loc="upper center", bbox_to_anchor=(0.5, 0.5),
            facecolor='#384780',  # Fond de la légende
            edgecolor='white',  # Bordure de la légende
            labelcolor='white',  # Couleur des étiquettes
            title_fontsize=12
        )
        legend.set_visible(False)

        def on_hover(event):
            if event.inaxes == plt.gca():
                legend.set_visible(True)
            else:
                legend.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)
        

        # Ajustement de la disposition
        plt.tight_layout()
        return fig



    def plot_victimes_par_localisation_et_gravite(self):
        df = pd.read_excel(self.file_path, engine="openpyxl", sheet_name="Victimes_2016_2017")

        categories = ['TUES', 'BLESSES GRAVES', 'BLESSES LEGERS']
        locations = ['EN AGGLOMERATION', 'HORS AGGLOMERATION']

        sizes = [
            df.loc[(df['TYPE'] == 'EN AGGLOMERATION'), 'TUES'].sum(),
            df.loc[(df['TYPE'] == 'EN AGGLOMERATION'), 'BLESSES GRAVES'].sum(),
            df.loc[(df['TYPE'] == 'EN AGGLOMERATION'), 'BLESSES LEGERS'].sum(),
            df.loc[(df['TYPE'] == 'HORS AGGLOMERATION'), 'TUES'].sum(),
            df.loc[(df['TYPE'] == 'HORS AGGLOMERATION'), 'BLESSES GRAVES'].sum(),
            df.loc[(df['TYPE'] == 'HORS AGGLOMERATION'), 'BLESSES LEGERS'].sum(),
        ]

        labels = [
            'TUES - EN AGGLOMERATION', 
            'BLESSES GRAVES - EN AGGLOMERATION',
            'BLESSES LEGERS - EN AGGLOMERATION',
            'TUES - HORS AGGLOMERATION',
            'BLESSES GRAVES - HORS AGGLOMERATION',
            'BLESSES LEGERS - HORS AGGLOMERATION',
        ]

        colors = ['#1f77b4', '#5da5da', '#aec7e8', '#ff7f0e', '#ff9d57', '#ffbb78']
        explode = [0.02, 0.02, 0, 0.2, 0.1, 0.070]

        
        fig = plt.figure(figsize=(6, 5))
        plt.gcf().set_facecolor('#231E6D')
        plt.gca().set_facecolor('#231E6D')

        
        wedges, texts, autotexts = plt.pie(
            sizes,
            autopct='%1.1f%%',
            startangle=110,
            explode=explode,
            colors=colors,
            textprops={'color': 'white'}
        )

        # Ajouter un titre
        plt.title("Victimes par Localisation et Gravité", fontsize=12, color='white')

        # Ajouter une légende
        legend = plt.legend(
            wedges, labels, 
            title="Catégories", 
            loc="upper center", bbox_to_anchor=(0.5, 0.5),
            facecolor='#384780', edgecolor='white', labelcolor='white', title_fontsize=10
        )
        legend.set_visible(False)  
        
        def on_hover(event):
            if event.inaxes == plt.gca():
                legend.set_visible(True) 
            else:
                legend.set_visible(False)  
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)  

        plt.tight_layout()
        return fig

        

    def plot_accidents_par_population(self):
        df = pd.read_excel(self.file_path, engine="openpyxl", sheet_name="accid_popul_region")
        df = df.iloc[:12, :].set_index('region')
        df_sorted = df.sort_values(by='population', ascending=False)

        pop_sizes = [pop / 10000 for pop in df_sorted['population']]
        colors=['red','#FFCC00','#FFCC00','#FFCC00','red','#FFCC00','#FFCC00','#FFCC00','#FFCC00','#FFCC00','#FFCC00','red']

        plt.figure(figsize=(8, 4.7))
        plt.gcf().set_facecolor('#231E6D')
        plt.gca().set_facecolor('#231E6D')

        for i, region in enumerate(df_sorted.index):
            plt.scatter(i, df_sorted['accidents'][i], s=pop_sizes[i], color=colors[i], alpha=0.5, label=region)

        plt.xticks(ticks=range(len(df_sorted.index)), labels=df_sorted.index, fontsize=6, color='white', rotation=45)
        plt.yticks(color='white',rotation=45)
        plt.xlabel('Régions', fontsize=12, color='white')
        plt.ylabel('Accidents', fontsize=12, color='white')
        plt.title('Accidents par Région (Triées par Population)', fontsize=12, color='white')
        plt.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
        plt.tight_layout()
        return plt.gcf()
        
    def plot_accidents_par_categorie_casa(self):
        data = pd.read_excel(self.file_path, sheet_name='ACCI_CASA')
        data.columns = ['City', 'Total_Accidents']
        data.dropna(inplace=True)
        data['Total_Accidents'] = pd.to_numeric(data['Total_Accidents'], errors='coerce')
        data.dropna(subset=['Total_Accidents'], inplace=True)
        data.sort_values(by='Total_Accidents', ascending=False, inplace=True)

        plt.figure(figsize=(6, 6), facecolor='#231E6D')
        ax = plt.gca()
        ax.set_facecolor('#231E6D')
        plt.barh(data['City'], data['Total_Accidents'], color='#f57659')
        plt.xlabel("Nombre d'Accidents", color='white')
        plt.title("Accidents par Ville", color='white',weight='bold')
        plt.xticks(color='white')
        plt.yticks(color='white',fontsize=6)
        plt.grid(axis='x', linestyle='--', alpha=0.7, color='white')
        plt.tight_layout()
        return plt.gcf()

    def plot_evolution_des_accidents_casa(self):
        data = pd.read_excel(self.file_path, sheet_name='CAUSE_ACC_CASA')
        sizes = data['Pourcentage Approximatif (%)']
        labels = data['Cause des Accidents']

        colors = ['#872274', '#cb3f69', '#f57659', '#ffb652',
                  '#f9f871', '#7ebf5a', '#4287f5', '#ff65a3', '#7f3f98', '#5bc0eb']
        explode = [0.1] * len(sizes)

        fig=plt.figure(figsize=(6, 6))
        wedges, texts, autotexts = plt.pie(
            sizes,
            labels=None,
            autopct='%1.1f%%',
            explode=explode,
            colors=colors[:len(sizes)],
            startangle=90,
            wedgeprops={'linewidth': 1.2},
            textprops={'fontsize': 10, 'color': 'white'}
        )
        plt.gca().set_facecolor('#231E6D')
        plt.gcf().patch.set_facecolor('#231E6D')

        
        plt.title("Répartition des Causes des Accidents", fontsize=12, color='white',weight='bold')
        legend = plt.legend(
            wedges, labels, 
            title="Causes des Accidents", 
            loc="upper center", bbox_to_anchor=(0.5, 0.5),
            facecolor='#384780', edgecolor='white', labelcolor='white', title_fontsize=12
        )
        legend.set_visible(False)  

        def on_hover(event):
            if event.inaxes == plt.gca():
                legend.set_visible(True)  
            else:
                legend.set_visible(False)  
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)  
        plt.tight_layout()
        return plt.gcf()


    def plot_accidents_par_jours_casa(self):
        data = pd.read_excel(self.file_path, sheet_name='LESROUTES_CASA', engine='openpyxl', skiprows=1)
        data.columns = [
            "Type_Reseau",
            "Circulation",
            "Accidents_Non_Mortels",
            "Accidents_Mortels",
        ]
        data.dropna(inplace=True)
        data = data[~data["Type_Reseau"].str.contains("TOTAL", na=False)]
        for col in ["Circulation", "Accidents_Non_Mortels", "Accidents_Mortels"]:
            data[col] = pd.to_numeric(data[col], errors='coerce')

        # Définition des couleurs
        colors = ['#cb3f69', '#00c89f', '#ffb652', '#0074D9', '#FF4136']  # Liste de couleurs
        color_mapping = {type_reseau: colors[i % len(colors)] for i, type_reseau in enumerate(data["Type_Reseau"])}

        # Création de la figure
        fig, ax1 = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor('#231E6D')
        ax1.set_facecolor('#231E6D')

        # Histogramme avec des couleurs différentes
        ax1.bar(
            data["Type_Reseau"],
            data["Circulation"],
            color=[color_mapping[type_reseau] for type_reseau in data["Type_Reseau"]],
            alpha=0.7,
        )

        # Suppression des labels de l'axe des x
        ax1.set_xticks([])

        # Deuxième axe pour les lignes
        ax2 = ax1.twinx()
        ax2.set_facecolor('#231E6D')
        ax2.plot(
            data["Type_Reseau"],
            data["Accidents_Non_Mortels"],
            color="#00c89f",
            marker="o",
            label="Accidents Non Mortels",
        )
        ax2.plot(
            data["Type_Reseau"],
            data["Accidents_Mortels"],
            color="#ffb652",
            marker="x",
            label="Accidents Mortels",
        )

        # Paramètres des axes
        ax1.set_ylabel("Circulation (Millions Veh.km/j)", color="white")
        ax2.set_ylabel("Nombre d'Accidents", color="white")

        ax1.tick_params(axis='y', colors='white')
        ax2.tick_params(axis='y', colors='white')

        # Titre
        plt.title(
            "Circulation et Accidents Mortels/Non Mortels par Type de Réseau Routier",
            color="white", fontsize=6, weight='bold'
        )
        
        # Création de la légende
        legend_elements = [
            plt.Line2D([0], [0], marker='s', color=color_mapping[type_reseau], label=type_reseau, markersize=10, linestyle='None')
            for type_reseau in data["Type_Reseau"]
        ]
        legend=plt.legend(handles=legend_elements, title="Type de Réseau", loc="upper right", fontsize=8,facecolor='#384780', edgecolor='white', labelcolor='white')
        legend.set_visible(False)  

        def on_hover(event):
            if event.inaxes == plt.gca():  
                legend.set_visible(True) 
            else:
                legend.set_visible(False)  
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)  
        
        plt.tight_layout()
        return fig

    
    def plot_accidents_par_categorie_tng(self):
        sheet_name = 'Sheet1'
        data = pd.read_excel(self.file_path, sheet_name=sheet_name)

        # Trier les données par nombre de décès pour un affichage clair
        data = data.sort_values(by="Décès", ascending=True)

        # Extraire les catégories et le nombre de décès
        categories = data["Catégorie"]
        deces = data["Décès"]

        # Création d'un graphique en barres horizontal
        fig, ax = plt.subplots(figsize=(5, 6))
        fig.patch.set_facecolor('#231E6D')
        ax.set_facecolor('#231E6D')

        y_positions = np.arange(len(categories))  # Positions des barres sur l'axe y
        ax.barh(y_positions, deces, color="#FF4500", edgecolor="orange")

        # Ajouter les noms des catégories sur l'axe y
        ax.set_yticks(y_positions)
        ax.set_yticklabels(categories, color='white', fontsize=6,rotation=45)

        # Ajouter un titre et des labels d'axes
        ax.set_title("Distribution des Décès par Catégorie", fontsize=10, weight='bold', color='white')
        ax.set_xlabel("Nombre de Décès", fontsize=8, weight='bold', color='white')
        ax.set_ylabel("Catégories", fontsize=8, weight='bold', color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        plt.tight_layout()
        return fig

    def plot_accidents_par_cause_tng(self):
        sheet_name = 'Sheet2'
        feuil2_data = pd.read_excel(self.file_path, sheet_name=sheet_name)

        sizes = feuil2_data["nbr acc"]
        aleend = feuil2_data["causes"]

        colors = ['#FF4500', '#1E90FF', '#FF6347', '#FFD700', '#2E8B57', '#4682B4']
        explode = [0.1] * len(sizes)

        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor('#231E6D')
        ax.set_facecolor('#231E6D')

        wedges, texts, autotexts = ax.pie(
            sizes,
            colors=colors,
            explode=explode,
            autopct='%1.1f%%',
            textprops={'color': 'white'},
        )
        
        legend=plt.legend(
           wedges, aleend,
            title="Causes des Accidents",
            loc="upper center", bbox_to_anchor=(0.5, 0.5),
            facecolor='#384780',  # Fond de la légende
            edgecolor='white',  # Bordure de la légende
            labelcolor='white',  # Couleur des étiquettes
            title_fontsize=12
        )
        legend.set_visible(False)  
        def on_hover(event):
            if event.inaxes == plt.gca():  
                legend.set_visible(True)  
            else:
                legend.set_visible(False)  
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover) 

        plt.title("Répartition des Accidents par Cause", fontsize=12, color='white',weight='bold')
        plt.tight_layout()
        return fig

    def plot_accidents_par_villes_tng(self):
        sheet_name = 'Sheet7'
        data = pd.read_excel(self.file_path, sheet_name=sheet_name)

        data.columns = ['City', 'Accid_N_Mort', 'Accid_Mort', 'Total_Accidents']
        data = data[['City', 'Total_Accidents']]
        data.dropna(inplace=True)
        data['Total_Accidents'] = pd.to_numeric(data['Total_Accidents'], errors='coerce')
        data.sort_values(by='Total_Accidents', ascending=False, inplace=True)

        fig, ax = plt.subplots(figsize=(5, 6))
        fig.patch.set_facecolor('#231E6D')
        ax.set_facecolor('#231E6D')

        ax.barh(data['City'], data['Total_Accidents'], color='yellow', edgecolor='black')

        ax.set_xlabel('Totale des Accidents', fontsize=10, color='white',weight='bold')
        ax.set_ylabel('Villes', fontsize=10, color='white',weight='bold')
        ax.set_title('Accidents par Ville', fontsize=12, color='white',weight='bold')

        ax.tick_params(colors='black', which='both')
        plt.yticks(color='white',fontsize=6,rotation=45)
        plt.xticks(color='white')

        plt.tight_layout()
        return fig

    def plot_accidents_par_categorie_dakhla(self):
        df = pd.read_excel(self.file_path, engine="openpyxl", sheet_name="ACCID_AGLO_DAKHLA_OUED_EDDAHAB")
        df = df[df['CATEGORIE'] != 'TOTAL']

        total_accidents = df["ACCID N.MORT"].sum() + df["ACCID MORT"].sum()
        df["Total_Cat"] = df["ACCID N.MORT"] + df["ACCID MORT"]
        df["Percentage"] = (df["Total_Cat"] / total_accidents) * 100

        categories = df["CATEGORIE"].tolist()
        values_outer = df["Total_Cat"].tolist()
        values_inner = df[["ACCID N.MORT", "ACCID MORT"]].values.flatten().tolist()

        
        outer_colors = ['#FF6500', '#6895D2']
        inner_colors = ['#FF3C00', '#F9FFA5', '#4682B4', '#ADD8E6']

        fig, ax = plt.subplots(figsize=(4, 6))
        fig.patch.set_facecolor('#231E6D')
        ax.set_facecolor('#231E6D')

        ax.pie(values_outer, radius=1.1, colors=outer_colors, startangle=90,
               wedgeprops=dict(width=0.27, edgecolor='w'))

        wedges_inner, texts_inner, autotexts_inner = ax.pie(
            values_inner, radius=0.7, colors=inner_colors, startangle=90,
            wedgeprops=dict(width=0.27, edgecolor='w'), autopct='%1.1f%%',
            textprops={'color': 'white'})

        agglomeration_data = df[df['CATEGORIE'] == 'EN AGGLOMERATION']
        if not agglomeration_data.empty:
            agglomeration_text = (
                f"En Agglomération: {int(agglomeration_data['Total_Cat'].sum())} accidents "
                f"({agglomeration_data['Percentage'].sum():.1f}%)"
            )
            """plt.annotate(
                agglomeration_text, xy=(0, -1.2), color='white', fontsize=10,
                ha='center', bbox=dict(facecolor='#384780', edgecolor='white', boxstyle='round')
            ) """

        hors_agglomeration_data = df[df['CATEGORIE'] == 'HORS AGGLOMERATION']
        if not hors_agglomeration_data.empty:
            hors_agglomeration_text = (
                f"Hors Agglomération: {int(hors_agglomeration_data['Total_Cat'].sum())} accidents "
                f"({hors_agglomeration_data['Percentage'].sum():.1f}%)"
            )
            """"
            plt.annotate(
                hors_agglomeration_text, xy=(0, -1.7), color='white', fontsize=8,
                ha='center', bbox=dict(facecolor='#384780', edgecolor='white', boxstyle='round')
            ) """

        legend_labels = (
            [f'{cat} (Total)' for cat in categories] +
            [f'{cat} - Non Mortels' for cat in categories] +
            [f'{cat} - Mortels' for cat in categories]
        )
        
        legend_wedges = wedges_inner
        legend=plt.legend(
            legend_wedges, legend_labels,
            title="Catégories et Sous-Catégories",
            loc="center right", bbox_to_anchor=(1, 0.5),
            facecolor='#384780', edgecolor='white', labelcolor='white', title_fontsize=10
        )
        
        legend.set_visible(False)  

        def on_hover(event):
            if event.inaxes == plt.gca(): 
                legend.set_visible(True)  
            else:
                legend.set_visible(False)  
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)  
        

        plt.title("Accidents à Dakhla Ouad Eddahab \n (Catégorie et Sous-Catégorie)", fontsize=11, color='white',weight='bold')
        plt.tight_layout()
        return fig

    def plot_3d_victimes_dakhla(self):
        df = pd.read_excel(self.file_path, engine="openpyxl", sheet_name="ACCID_AGLO_DAKHLA_OUED_EDDAHAB")
        df = df[df['CATEGORIE'] != 'TOTAL']

        categories = df["CATEGORIE"].tolist()
        tues = df["TUES"].tolist()
        blesse_legers = df["BLESSE LEGERS"].tolist()
        blesse_graves = df["BLESSE GRAVES"].tolist()

        bar_width = 0.3
        locations = np.arange(len(categories))
        text_color = 'white'

        fig = plt.figure(figsize=(6, 6), facecolor='#231E6D')
        ax = fig.add_subplot(111, projection='3d')

        ax.set_facecolor('#231E6D')

        ax.bar(locations, tues, zs=0, zdir='y', width=bar_width, color='red', alpha=1, label='Tués')
        ax.bar(locations, blesse_legers, zs=1, zdir='y', width=bar_width, color='orange', alpha=1, label='Blessés Légers')
        ax.bar(locations, blesse_graves, zs=2, zdir='y', width=bar_width, color='yellow', alpha=1, label='Blessés Graves')

        ax.set_xlabel('Location', color=text_color, fontsize=8)
        ax.set_ylabel('Categories', color=text_color, fontsize=8)
        ax.set_zlabel('Nombre des cas', fontsize=8, color=text_color)

        ax.set_title("Victimes à Dakhla Oued Eddahab", fontsize=12, color=text_color, loc='center', pad=2,weight='bold')

        ax.set_yticks([0, 1, 2])

        ax.set_xticks(locations)
        ax.set_xticklabels(categories, fontsize=8, rotation=45, ha='right', color=text_color)

        legend = ax.legend(title="Catégories", facecolor='#231E6D', edgecolor='white', fontsize=10, title_fontsize=12)
        legend.set_visible(False)  

        def on_hover(event):
            if event.inaxes == plt.gca():  
                legend.set_visible(True) 
            else:
                legend.set_visible(False)  
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)  
        
        for text in legend.get_texts():
            text.set_color(text_color)

        return fig

    def plot_accidents_par_conditions_meteo_dakhla(self):
        df = pd.read_excel(self.file_path, engine="openpyxl", sheet_name="ACCID_METEO_DAKHLA")

        categories = df["Condition Météo"]
        accidents_totaux = df["Accidents Totaux"]
        accidents_mortels = df["Accidents Mortels"]
        accidents_non_mortels = df["Accidents Non Mortels"]

        fig, ax = plt.subplots(figsize=(5, 6))
        fig.patch.set_facecolor('#231E6D')
        ax.set_facecolor('#231E6D')

        ax.barh(categories, accidents_totaux, label="Accidents Totaux", color="grey", alpha=0.5)
        ax.barh(categories, accidents_mortels, label="Accidents Mortels", color="red")
        ax.barh(categories, accidents_non_mortels, left=accidents_mortels, label="Accidents Non Mortels", color="orange")

        ax.set_title("Répartition des accidents\n en fonction des conditions météorologiques", fontsize=10, color='white', loc='center', pad=2,weight='bold')
        ax.set_xlabel("Nombre d'Accidents", fontsize=8, color='white')
        ax.set_ylabel("Conditions Météorologiques", fontsize=9, color='white')
        ax.tick_params(colors='white')
        
        legend = ax.legend(title="Gravité", loc="lower right", facecolor='#231E6D', edgecolor='white', labelcolor='white',)
        legend.set_visible(False)

        def on_hover(event):
            if event.inaxes == ax:
                legend.set_visible(True)
            else:
                legend.set_visible(False)
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", on_hover)

        plt.tight_layout()
        return fig
