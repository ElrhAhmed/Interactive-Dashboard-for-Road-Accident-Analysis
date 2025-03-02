from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import sys
import tkinter as tk
import tkintermapview
import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from shapely.geometry import Point

colormap = 'rainbow'
class Accidents_Map:
    
    #methode pour afficher la carte des accidents
    def __init__(self, parent, geojson_path, data, x, y, width, height):
        self.geojson_path = geojson_path
        self.df_data = pd.DataFrame(data)
        self.frame = tk.Frame(parent, width=width, height=height, bg="white")
        self.frame.place(x=x, y=y)

        # Charger les données GeoJSON
        self.gdf_map = gpd.read_file(self.geojson_path)
        if "region" not in self.gdf_map.columns:
            raise ValueError("La colonne 'region' est manquante dans le fichier GeoJSON.")

        # Joindre les données
        self.gdf_map = self.gdf_map.set_index("region").join(self.df_data.set_index("region"))

        # Préparer le widget map
        self.map_widget = tkintermapview.TkinterMapView(self.frame, width=width, height=height, corner_radius=0)
        self.map_widget.pack(fill=tk.BOTH, expand=True)

        # Label de survol
        self.hover_label = tk.Label(parent, bg="white", relief=tk.SOLID, borderwidth=1)
        self.hover_label.place_forget()  # Masquer le label au début

        self.setup_map()
        self.add_legend()
        self.map_widget.canvas.bind("<Motion>", self.on_hover)  # Événement de survol
      
    
    def setup_map(self):
        self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        self.map_widget.set_position(31.7917, -7.0926)
        self.map_widget.set_zoom(6)

        min_val = self.gdf_map['accidents'].min()
        max_val = self.gdf_map['accidents'].max()

        cmap = plt.colormaps.get(colormap)

        # Couleurs personnalisées pour certaines régions
        custom_colors = {
            'Casablanca-Settat': '#FF2929',  
            'Tanger-Tetouan-Hoceima': '#78B3CE',  
            'Dakhla-Oued Eddahab': '#ECE852',  
        }

        for idx, row in self.gdf_map.iterrows():
            geom = row['geometry']
            if geom is None or geom.is_empty:
                continue

            
            region_name = idx
            outline_color = "black"
            if region_name in custom_colors:
                outline_color = "red"
    
            accidents = row['accidents']
            if pd.isnull(accidents):
                continue
            ratio = (accidents - min_val) / (max_val - min_val) if max_val != min_val else 0
            color_rgba = cmap(ratio)
            color_hex = mcolors.to_hex(color_rgba)

            if geom.geom_type == 'Polygon':
                self._draw_polygon(geom, color_hex, outline_color)
            elif geom.geom_type == 'MultiPolygon':
                for poly in geom.geoms:
                    self._draw_polygon(poly, color_hex, outline_color)
    #methode pour dessiner un polygone
    def _draw_polygon(self, polygon, fill_color, outline_color = "black"):
        coords = list(polygon.exterior.coords)
        coords_latlon = [(y, x) for x, y in coords]
        self.map_widget.set_polygon(coords_latlon, fill_color=fill_color, border_width=0.6, outline_color=outline_color)
    
    #methode pour afficher les informations de survol
    def on_hover(self, event):
        x_hover, y_hover = event.x, event.y
        lat, lon = self.map_widget.convert_canvas_coords_to_decimal_coords(x_hover, y_hover)

        # Afficher les coordonnées de survol
        print(f"Hover: Canvas({x_hover}, {y_hover}) -> LatLon({lat}, {lon})")

        point = Point(lon, lat)
        for idx, row in self.gdf_map.iterrows():
            geom = row['geometry']
            if geom is not None and not geom.is_empty and geom.contains(point):
                region_name = idx
                population = row.get('population', 'N/A')
                accidents = row.get('accidents', 'N/A')
                victims = row.get('victims', 'N/A')
                self.update_hover_label(region_name, population, accidents, victims, x_hover, y_hover)
                return  # Sortir de la boucle si un match est trouvé
        self.hover_label.place_forget()  # Masquer le label si aucun match n'est trouvé

    def update_hover_label(self, region_name, population, accidents, victims, x, y):
        text = (
            f"Région: {region_name}\n"
            f"Population: {population}\n"
            f"Accidents: {accidents}\n"
            f"Victimes: {victims}"
        )
        self.hover_label.config(text=text, bg="white", font=("Arial", 10))
        self.hover_label.place(x=x + 1400, y=y + 448)
    #methode pour ajouter une légende
    def add_legend(self):
        legend_frame = tk.Frame(self.frame, bg="white", relief=tk.SOLID, borderwidth=1)
        legend_frame.place(relx=0.98, rely=0.98, anchor=tk.SE)

        legend_title = tk.Label(legend_frame, text="Legend", font=("Arial", 12, "bold"), bg="white")
        legend_title.pack(pady=5)

        gradient_canvas = tk.Canvas(legend_frame, width=150, height=20, bg="white", highlightthickness=0)
        gradient_canvas.pack()

        cmap = mcolors.LinearSegmentedColormap.from_list("rainbow", ['blue', 'green', 'yellow', 'red'])
        for i in range(150):
            ratio = i / 150
            color = mcolors.to_hex(cmap(ratio))
            gradient_canvas.create_line(i, 0, i, 20, fill=color)

        gradient_label = tk.Label(legend_frame, text="Low   Accidents   High", bg="white", font=("Arial", 8))
        gradient_label.pack()

    def run(self):
        self.root.mainloop()

