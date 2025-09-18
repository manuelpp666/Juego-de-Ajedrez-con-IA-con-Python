import pygame
from gui.board import draw_board, highlight_square, highlight_king_in_check
from gui.pieces import load_images, IMAGES
from chessLogic.chessboard import ChessBoard
from chessLogic.move import Move
from IA.search import get_best_move



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

def modal_game_over(screen, message, board):
    """
    Muestra un modal con el mensaje de jaque mate y opciones.
    Recibe 'board' para poder redibujar el tablero congelado de fondo.
    """
    import sys

    font = pygame.font.SysFont("Arial", 36, bold=True)
    small_font = pygame.font.SysFont("Arial", 28)

    play_again_rect = pygame.Rect(200, 350, 240, 50)
    exit_rect = pygame.Rect(200, 420, 240, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if play_again_rect.collidepoint(x, y):
                    # limpiar eventos residuales antes de salir del modal
                    pygame.event.clear()
                    return "play_again"
                elif exit_rect.collidepoint(x, y):
                    pygame.quit()
                    sys.exit()

        # Redibujar tablero y piezas (estado congelado)
        draw_board(screen)
        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece != "--":
                    screen.blit(IMAGES[piece], (c * SQ_SIZE, r * SQ_SIZE))

        # Fondo semi-transparente encima del tablero
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))

        # Texto principal
        text = font.render(message, True, (255, 255, 255))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))

        # Botón "Jugar de nuevo"
        pygame.draw.rect(screen, (0, 200, 0), play_again_rect)
        play_text = small_font.render("Jugar de nuevo", True, (255, 255, 255))
        screen.blit(play_text, (play_again_rect.centerx - play_text.get_width()//2,
                                play_again_rect.centery - play_text.get_height()//2))

        # Botón "Salir"
        pygame.draw.rect(screen, (200, 0, 0), exit_rect)
        exit_text = small_font.render("Salir", True, (255, 255, 255))
        screen.blit(exit_text, (exit_rect.centerx - exit_text.get_width()//2,
                                exit_rect.centery - exit_text.get_height()//2))

        pygame.display.flip()

def modal_choose_mode(screen):
    """
    Modal inicial: elegir jugar contra Humano o IA.
    Retorna 'human' o 'ia'.
    """
    import sys
    font = pygame.font.SysFont("Arial", 36, bold=True)

    human_rect = pygame.Rect(200, 250, 240, 50)
    ia_rect = pygame.Rect(200, 320, 240, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if human_rect.collidepoint(x, y):
                    return "human"
                elif ia_rect.collidepoint(x, y):
                    return "ia"

        # Fondo
        screen.fill((0, 0, 0))

        # Texto principal
        text = font.render("Elige modo de juego", True, (255, 255, 255))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 150))

        # Botón Humano
        pygame.draw.rect(screen, (0, 200, 0), human_rect)
        h_text = font.render("Humano vs Humano", True, (255, 255, 255))
        screen.blit(h_text, (human_rect.centerx - h_text.get_width()//2,
                             human_rect.centery - h_text.get_height()//2))

        # Botón IA
        pygame.draw.rect(screen, (200, 0, 0), ia_rect)
        ia_text = font.render("Humano vs IA", True, (255, 255, 255))
        screen.blit(ia_text, (ia_rect.centerx - ia_text.get_width()//2,
                              ia_rect.centery - ia_text.get_height()//2))

        pygame.display.flip()


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ajedrez con IA: PHIA")

    clock = pygame.time.Clock()
    board = ChessBoard()
    load_images()

    # 🔹 Preguntar modo antes de iniciar
    mode = modal_choose_mode(screen)  # ← 'ia' o 'human'

    selected_square = None
    running = True

    # --- Control para que la IA piense sólo UNA vez por turno ---
    last_turn = board.turn  # guardamos el turno anterior; si cambia a 'b' llamamos a la IA una vez

    while running:
        # --- 1) Procesar eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Turno humano (si corresponde)
            if mode == "human" or (mode == "ia" and board.turn == "w"):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    col = x // SQ_SIZE
                    row = y // SQ_SIZE

                    if selected_square is None:
                        if board.get_piece(row, col) != "--":
                            selected_square = (row, col)
                    else:
                        start = selected_square
                        end = (row, col)
                        piece = board.get_piece(*start)

                        if board.is_valid_move(start, end):
                            promote_to = None
                            if piece[1] == "p" and (end[0] == 0 or end[0] == 7):
                                promote_to = promotion_menu(screen, piece[0])

                            turno_actual = board.turn
                            move = Move(start, end, board, promotion_choice=promote_to or "q")
                            board.make_move(move)

                            # actualizar pantalla inmediatamente para mostrar tu jugada
                            draw_board(screen)
                            if board.is_check(board.turn):
                                if board.turn == "w":
                                    king_row, king_col = board.white_king_pos
                                else:
                                    king_row, king_col = board.black_king_pos
                                from gui.board import highlight_king_in_check
                                highlight_king_in_check(screen, king_row, king_col)
                            for r in range(8):
                                for c in range(8):
                                    piece_draw = board.get_piece(r, c)
                                    if piece_draw != "--":
                                        screen.blit(IMAGES[piece_draw], (c * SQ_SIZE, r * SQ_SIZE))
                            pygame.display.flip()

                            # Verificar jaque mate
                            rival = board.turn
                            if board.is_checkmate(rival):
                                ganador = "Blancas" if turno_actual == "w" else "Negras"
                                action = modal_game_over(screen, f"¡Jaque Mate! Ganaron las {ganador}", board)
                                if action == "play_again":
                                    board = ChessBoard()
                                    selected_square = None
                                    last_turn = board.turn

                        selected_square = None

        # --- 2) Turno de la IA: fuera del for-event, y SOLO si acabó de cambiar a turno IA ---
        # Si modo IA y ahora es turno de las negras y antes NO era turno de negras, llamamos 1 vez.
        if mode == "ia" and board.turn == "b" and last_turn != board.turn and running:
            
            best_move = get_best_move(board, max_depth=2)
            if best_move:
                board.make_move(best_move)

                # Verificar jaque mate
                if board.is_checkmate("w"):
                    action = modal_game_over(screen, "¡Jaque Mate! Ganaron las Negras", board)
                    if action == "play_again":
                        board = ChessBoard()
                        selected_square = None

        # Actualizamos last_turn para la siguiente iteración
        last_turn = board.turn

        # --- 3) Dibujar pantalla ---
        draw_board(screen)
        if board.is_check(board.turn):
            if board.turn == "w":
                king_row, king_col = board.white_king_pos
            else:
                king_row, king_col = board.black_king_pos
            from gui.board import highlight_king_in_check
            highlight_king_in_check(screen, king_row, king_col)

        if selected_square is not None:
            highlight_square(screen, selected_square[0], selected_square[1])

        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece != "--":
                    screen.blit(IMAGES[piece], (col * SQ_SIZE, row * SQ_SIZE))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


