import os
import pygame

# Diccionario global para guardar las imágenes
IMAGES = {}

# Nombres de las piezas (usaremos notación FEN: wp = white pawn, bk = black king, etc.)
PIECE_NAMES = ["wp", "wr", "wn", "wb", "wq", "wk",
               "bp", "br", "bn", "bb", "bq", "bk"]

def load_images():
    """
    Carga las imágenes de assets/ y las guarda en el diccionario IMAGES.
    """
    base_path = os.path.join(os.path.dirname(__file__), "..", "assets")
    for piece in PIECE_NAMES:
        path = os.path.join(base_path, f"{piece}.png")
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(path), (80, 80)  # ajusta tamaño según tu cuadrado
        )
