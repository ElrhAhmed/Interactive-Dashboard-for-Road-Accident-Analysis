import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt

# Classe pour la fenêtre contenant la carte ADM Trafic 
class Live_map(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADM Trafic Map")

        # Définir la taille de la fenêtre
        self.resize(1200, 800)

        # Ajouter le QWebEngineView pour afficher la carte ADM Trafic
        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://admtrafic.ma/?map=true"))
        self.setCentralWidget(self.browser)

    # Fonction pour ouvrir la carte ADM Trafic
    def open_adm_trafic_map():
        
        qt_app = QApplication.instance() or QApplication(sys.argv)

        # Créer et afficher la fenêtre
        map_window = Live_map()
        map_window.show()

        # Si l'application PySide6 n'est pas encore démarrée, démarrer la boucle d'événements
        if not QApplication.instance().closingDown():
            qt_app.exec()