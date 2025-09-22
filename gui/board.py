"""
Módulo de interfaz gráfica para el juego de ajedrez.

Este archivo contiene la clase y funciones necesarias para
mostrar el tablero y manejar la interacción del usuario con la GUI.
"""
import pygame

# Tamaño del tablero
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colores (actualizados para un look más moderno)
LIGHT_SQUARE_COLOR = (238, 238, 210) # Un blanco crema
DARK_SQUARE_COLOR = (118, 150, 86)   # Un verde oscuro/marrón
HIGHLIGHT_COLOR = (186, 202, 43, 150) # Verde amarillento semi-transparente
CHECK_COLOR = (255, 50, 50, 150)     # Rojo más vibrante semi-transparente

def draw_board(win):
    """
    Dibuja el tablero de ajedrez en la ventana principal.

    Args:
        screen (pygame.Surface): superficie de Pygame donde se dibuja el tablero.
    """
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_SQUARE_COLOR if (row + col) % 2 == 0 else DARK_SQUARE_COLOR
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlight_square(win, row, col):
    """
    Resalta la casilla seleccionada.
    """
    if row is not None and col is not None:
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill(HIGHLIGHT_COLOR)
        win.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def highlight_king_in_check(win, row, col):
    """
    Resalta la casilla del rey en rojo si está en jaque.
    """
    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    s.fill(CHECK_COLOR)
    win.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

