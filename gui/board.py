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

# Colores
WHITE = (245, 245, 220)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0, 100)  # Verde semi-transparente

def draw_board(win):
    """
    Dibuja el tablero de ajedrez en la ventana principal.

    Args:
        screen (pygame.Surface): superficie de Pygame donde se dibuja el tablero.
    """
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 == 1:
                pygame.draw.rect(win, BROWN, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlight_square(win, row, col):
    """
    Resalta la casilla seleccionada en verde.
    """
    if row is not None and col is not None:
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)  
        s.fill(GREEN)
        win.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
