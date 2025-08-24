import pygame
from gui.board import draw_board, highlight_square
from gui.pieces import load_images, IMAGES
from chessLogic.chessboard import ChessBoard

WIDTH, HEIGHT = 640, 640
SQ_SIZE = WIDTH // 8

def promotion_menu(screen, color):
    """
    Muestra opciones de promoción usando imágenes y devuelve la elección del jugador.
    color: 'w' o 'b'
    """
    import sys

    options = ['q', 'r', 'b', 'n']  # reina, torre, alfil, caballo
    running = True
    choice = None

    # Crear botones con posición
    buttons = []
    for i, opt in enumerate(options):
        rect = pygame.Rect(150 + i*80, 250, 60, 60)
        buttons.append((rect, color + opt))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                for rect, piece in buttons:
                    if rect.collidepoint(x, y):
                        choice = piece[1]  # letra q/r/b/n
                        running = False

        # Fondo semitransparente
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))

        # Dibujar botones con imágenes
        for rect, piece in buttons:
            pygame.draw.rect(screen, (255, 255, 255), rect)  # borde blanco
            img = IMAGES[piece]
            img_scaled = pygame.transform.scale(img, (rect.width, rect.height))
            screen.blit(img_scaled, rect.topleft)

        pygame.display.flip()

    return choice

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ajedrez con IA")

    clock = pygame.time.Clock()
    board = ChessBoard()  # estado del tablero
    load_images()         # carga piezas

    selected_square = None  # para guardar la casilla seleccionada
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Detectar clic
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // SQ_SIZE
                row = y // SQ_SIZE

                if selected_square is None:
                    # Primer clic -> seleccionar pieza
                    if board.get_piece(row, col) != "--":
                        selected_square = (row, col)
                else:
                    # Segundo clic -> mover pieza
                    start = selected_square
                    end = (row, col)
                    piece = board.get_piece(*start)

                    promote_to = "q"  # por defecto
                    if piece[1] == "p" and (end[0] == 0 or end[0] == 7):
                        promote_to = promotion_menu(screen, piece[0])

                    board.move_piece(start, end, promote_to=promote_to)
                    selected_square = None

        # 1. Dibuja tablero vacío
        draw_board(screen)

        # 2. Si hay selección, resáltala
        if selected_square is not None:
            highlight_square(screen, selected_square[0], selected_square[1])

        # 3. Dibuja piezas encima
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece != "--":
                    screen.blit(IMAGES[piece], (col * SQ_SIZE, row * SQ_SIZE))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
