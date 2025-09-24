"""
Módulo de interfaz gráfica para el juego de ajedrez.

Este archivo contiene la clase y funciones necesarias para
mostrar el tablero y manejar la interacción del usuario con la GUI.
"""
import pygame # Importa la biblioteca Pygame para gráficos y manejo de eventos.

# Tamaño del tablero y configuración de la ventana.
WIDTH, HEIGHT = 640, 640 # Ancho y alto de la ventana en píxeles.
ROWS, COLS = 8, 8 # Número de filas y columnas del tablero de ajedrez.
SQUARE_SIZE = WIDTH // COLS # Calcula el tamaño de cada casilla del tablero.

# Colores (actualizados para un look más moderno).
LIGHT_SQUARE_COLOR = (238, 238, 210) # Color para las casillas claras (crema).
DARK_SQUARE_COLOR = (118, 150, 86)   # Color para las casillas oscuras (verde oscuro/marrón).
HIGHLIGHT_COLOR = (186, 202, 43, 150) # Color para resaltar casillas seleccionadas (verde amarillento semi-transparente).
CHECK_COLOR = (255, 50, 50, 150)     # Color para resaltar el rey en jaque (rojo vibrante semi-transparente).

def draw_board(win):
    """
    Dibuja el tablero de ajedrez en la ventana principal.

    Args:
        screen (pygame.Surface): superficie de Pygame donde se dibuja el tablero.
    """
    for row in range(ROWS): # Itera sobre cada fila del tablero.
        for col in range(COLS): # Itera sobre cada columna del tablero.
            # Alterna los colores de las casillas para crear el patrón de ajedrez.
            color = LIGHT_SQUARE_COLOR if (row + col) % 2 == 0 else DARK_SQUARE_COLOR
            # Dibuja un rectángulo para cada casilla.
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlight_square(win, row, col):
    """
    Resalta la casilla seleccionada o las posibles casillas de destino.

    Args:
        win (pygame.Surface): La superficie de Pygame donde se dibujará el resaltado.
        row (int): La fila de la casilla a resaltar.
        col (int): La columna de la casilla a resaltar.
    """
    if row is not None and col is not None: # Asegura que se haya proporcionado una casilla válida.
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA) # Crea una superficie semi-transparente.
        s.fill(HIGHLIGHT_COLOR) # Rellena la superficie con el color de resaltado.
        win.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE)) # Dibuja la superficie resaltada en la posición de la casilla.

def highlight_king_in_check(win, row, col):
    """
    Resalta la casilla del rey en rojo si está en jaque.

    Args:
        win (pygame.Surface): La superficie de Pygame donde se dibujará el resaltado.
        row (int): La fila del rey.
        col (int): La columna del rey.
    """
    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA) # Crea una superficie semi-transparente.
    s.fill(CHECK_COLOR) # Rellena la superficie con el color de jaque.
    win.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE)) # Dibuja la superficie resaltada en la posición del rey.



