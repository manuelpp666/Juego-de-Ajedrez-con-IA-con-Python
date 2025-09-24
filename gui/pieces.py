import os # Importa el módulo os para interactuar con el sistema operativo (rutas de archivos).
import pygame # Importa la biblioteca Pygame para el manejo de imágenes.

# Diccionario global para guardar las imágenes de las piezas.
IMAGES = {}

# Nombres de las piezas (usaremos notación FEN simplificada: wp = white pawn, bk = black king, etc.)
PIECE_NAMES = ["wp", "wr", "wn", "wb", "wq", "wk", # Piezas blancas
               "bp", "br", "bn", "bb", "bq", "bk"] # Piezas negras

def load_images():
    """
    Carga las imágenes de la carpeta 'assets/' y las guarda en el diccionario IMAGES.
    Cada imagen se escala al tamaño de una casilla del tablero.
    """
    # Construye la ruta base a la carpeta 'assets'.
    # os.path.dirname(__file__) obtiene el directorio del archivo actual (pieces.py).
    # ".." sube un nivel al directorio raíz del proyecto.
    # "assets" entra en la carpeta de activos.
    base_path = os.path.join(os.path.dirname(__file__), "..", "assets")
    
    for piece in PIECE_NAMES: # Itera sobre cada nombre de pieza definido.
        # Construye la ruta completa al archivo de imagen de la pieza (ej. "assets/wp.png").
        path = os.path.join(base_path, f"{piece}.png")
        
        # Carga la imagen, la escala a 80x80 píxeles (ajusta según el tamaño de tu casilla)
        # y la almacena en el diccionario IMAGES usando el nombre de la pieza como clave.
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(path), (80, 80)  # ajusta tamaño según tu cuadrado (SQUARE_SIZE en board.py)
        )

