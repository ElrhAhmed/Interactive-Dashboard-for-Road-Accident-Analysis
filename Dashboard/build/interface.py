from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from visualisation import Visualisation_des_accidents
from mapc_accidents import Accidents_Map
from live_map import Live_map

base_dir = Path(__file__).parent  # Location of Main.py
file_path = base_dir.parent.parent / "accident_de_route_2017.xlsx" 
visualizer = Visualisation_des_accidents(file_path)

class interface:
    def __init__(self):
        # Créer une fenêtre principale
        self.window = Tk()
        self.window.geometry("1920x1080")
        self.window.configure(bg="#110E43")
        self.window.resizable(False, False)

        # chemin du fichier
        self.output_path = Path(__file__).parent
        self.assets_path = self.output_path / Path(r".\assets\frame0")

        # Créer un canvas

        self.canvas = Canvas(
            self.window,
            bg="#110E43",
            height=1080,
            width=1920,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        
        self.setup_ui()
        self.setup_buttons()
        
        self.display_graph_in_ui(visualizer.plot_accidents_par_categorie(), 1402, 100, 480, 290)
        self.display_graph_in_ui(visualizer.plot_evolution_des_accidents(), 27, 151, 622, 380)
        self.display_graph_in_ui(visualizer.plot_accidents_par_population(),678,100,702,431)
        self.display_graph_in_ui(visualizer.plot_victimes_par_categorie_usagers(), 466, 572, 473, 454)
            

        self.map_window = None  


    #methode pour ouvrir la carte ADM Trafic
    def open_adm_trafic_map(self):
        if not self.map_window: 
            self.map_window = Live_map()
            self.map_window.show()
        else:
            self.map_window.activateWindow()  # Réactiver si elle est déjà ouverte

     #methode pour afficher le graphique dans l'interface       
    def display_graph_in_ui(self, figure,x1,y1,w,h):
        canvas = FigureCanvasTkAgg(figure, master=self.window)
        canvas.get_tk_widget().place(x=x1, y=y1)  
        canvas.get_tk_widget().config(width=w, height=h)
        canvas.draw()
    
     #methode pour gerer le chemin des fichiers
    def relative_to_assets(self, path: str) -> Path:
        """Helper method to get paths relative to assets directory."""
        return self.assets_path / Path(path)
    
    
    def setup_ui(self):
        """Setup static UI components like text and images."""
        # ajouter les images
        image_image_1 = PhotoImage(file=self.relative_to_assets("image_1.png"))
        self.canvas.create_image(960.0, 44.0, image=image_image_1)

        self.canvas.create_text(
            107.0, 28.0,
            anchor="nw",
            text="ETUDE DES ACCIDENTS DE ROUTE AU MAROC",
            fill="#FFFFFF",
            font=("Inter SemiBold", 28 * -1)
        )

        #positionner les images
        images = [
           
            ("image_17.png", (1649.0, 740.0)),
            ("image_3.png", (1649.0, 256.0)),
            ("image_4.png", (1029.0, 320.0)),
            ("image_5.png", (343.0, 344.0)),
            ("image_6.png", (703.0, 800.0)),
            ("image_8.png", (243.0, 799.0)),
            ("image_9.png", (702.0, 799.0)),
            ("image_10.png", (1157.0, 799.0)),
            ("image_11.png", (64.0, 39.0)),
            ("image_14.png", (243, 799.0)),
            ("image_16.png", (1168.0, 799.0))
        ]

        for image_name, position in images:
            img = PhotoImage(file=self.relative_to_assets(image_name))
            self.canvas.create_image(*position, image=img)
            setattr(self, f"{image_name.split('.')[0]}_img", img)  
         
   
    # Intégrer la carte
        base_dir = Path(__file__).parent  # Location of Main.py
        geojson_path = base_dir.parent.parent / "morocco_regions.geojson"
        #geojson_path = "morocco_regions.geojson"
        data = {
            'region': [
                'Tanger-Tetouan-Hoceima', 'Oriental', 'Fes-Meknes', 'Rabat-Sale-Kenitra',
                'Beni Mellal-Khenifra', 'Casablanca-Settat', 'Marrakech-Safi', 'Daraa-Tafilelt',
                'Souss Massa', 'Guelmim-Oued Noun', 'Laayoune-Saguia Hamra', 'Dakhla-Oued Eddahab'
            ],
            'population': [3648200, 2283800, 4362900, 4654000, 2590000, 7284400, 4846100, 1632600, 2722000, 486200, 367700, 142800],
            'accidents': [6237, 4166, 9276, 15226, 5764, 27490, 11264, 2016, 5500, 959, 1137, 63],
            'victims': [1200, 900, 1400, 2100, 800, 3200, 1600, 450, 950, 200, 300, 20],
        }

        # Ajouter la carte à x=1401, y=484 avec w=497, h=516
        self.map_interface = Accidents_Map(self.window, geojson_path, data, x=1401, y=484, width=497, height=516)
    def setup_buttons(self):
        """Setup buttons with their images and commands."""
        buttons = [
            ("button_1.png", (1183.846, 16.912), (216.923, 61.445), lambda: self.on_button_click(1)),
            ("button_2.png", (1426.154, 16.912), (216.923, 61.445), lambda: self.on_button_click(2)),
            ("button_3.png", (1667.308, 16.912), (216.923, 61.445), lambda: self.on_button_click(3)),
            ("button_4.png", (33.806, 105.022), (306.578, 32.462), lambda: self.on_button_click(4)),
            ("button_5.png", (1401.0, 432.0), (244.615, 32.462), lambda: self.on_button_click(5)),
            ("button_6.png", (345.0, 105.022), (309.614, 32.462), lambda: self.on_button_click(6)),
            ("button_7.png", (1654.846, 432.0), (229.615, 32.462), lambda: self.on_button_click(7)),
            ("button_8.png", (1401, 1010.0), (497, 32.462), lambda: self.on_button_click(8))
        ]

        for i, (image_name, position, size, command) in enumerate(buttons, start=1):
            img = PhotoImage(file=self.relative_to_assets(image_name))
            button = Button(
                image=img,
                borderwidth=0,
                highlightthickness=0,
                command=command,
                relief="flat"
            )
            button.place(x=position[0], y=position[1], width=size[0], height=size[1])
            setattr(self, f"button_{i}_img", img)  

    #methode pour gérer les clics sur les boutons
    def on_button_click(self, button_id):
        
        if button_id == 1:
            self.display_graph_in_ui(visualizer.plot_3d_victimes_dakhla(), 44, 572, 399, 454)
            self.display_graph_in_ui(visualizer.plot_accidents_par_conditions_meteo_dakhla(), 465, 572, 473, 453)
            self.display_graph_in_ui(visualizer.plot_accidents_par_categorie_dakhla(), 958, 572, 399, 454)
        elif button_id == 2:
            self.display_graph_in_ui(visualizer.plot_accidents_par_categorie_tng(), 44, 572, 399, 454)
            self.display_graph_in_ui(visualizer.plot_accidents_par_cause_tng(), 465, 572, 473, 453)
            self.display_graph_in_ui(visualizer.plot_accidents_par_villes_tng(), 958, 572, 399, 454)
        elif button_id == 3:
            self.display_graph_in_ui(visualizer.plot_accidents_par_categorie_casa(), 958, 572, 399, 454)
            self.display_graph_in_ui(visualizer.plot_evolution_des_accidents_casa(),  44, 572, 399, 454)
            self.display_graph_in_ui(visualizer.plot_accidents_par_jours_casa(),465, 572, 473, 453)
        elif button_id == 4:
            self.display_graph_in_ui(visualizer.plot_evolution_des_accidents(), 27, 151, 622, 380)
        elif button_id == 5:
            self.display_graph_in_ui(visualizer.plot_accidents_par_categorie(), 1402, 100, 497, 312)
        elif button_id == 6:
            self.display_graph_in_ui(visualizer.plot_accidents_par_jours(), 27, 151, 632, 380)
        elif button_id == 7:
            self.display_graph_in_ui(visualizer.plot_victimes_par_localisation_et_gravite(), 1402, 100, 497, 312) 
        elif button_id == 8:  
            self.open_adm_trafic_map()


    
    #methode pour exécuter le mainloop de Tkinter
    def run(self):
        """Run the Tkinter mainloop."""
        self.window.mainloop()
        
