import pygame
from gui.board import draw_board, highlight_square, highlight_king_in_check
from gui.pieces import load_images, IMAGES
from chessLogic.chessboard import ChessBoard
from chessLogic.move import Move
from IA.search import get_best_move
import sys  # Importar sys para sys.exit()

WIDTH, HEIGHT = 640, 640
SQ_SIZE = WIDTH // 8

def promotion_menu(screen, color):
    """
    Muestra opciones de promoción usando imágenes y devuelve la elección del jugador.
    color: 'w' o 'b'
    """
    options = ['q', 'r', 'b', 'n']  # reina, torre, alfil, caballo
    running = True
    choice = None

    # Fondo semitransparente para el modal
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))  # Negro con 180 de transparencia
    screen.blit(s, (0, 0))

    # Dibujar un panel para las opciones
    panel_width = 400
    panel_height = 100
    panel_x = (WIDTH - panel_width) // 2
    panel_y = (HEIGHT - panel_height) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, (50, 50, 50), panel_rect, border_radius=10)  # Fondo oscuro para el panel
    pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3, border_radius=10)  # Borde claro

    font = pygame.font.SysFont("Arial", 24, bold=True)
    text_surface = font.render("Elige pieza para promocionar:", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, panel_y + 20))
    screen.blit(text_surface, text_rect)

    # Crear botones con posición
    buttons = []
    button_size = 60
    spacing = 20
    total_buttons_width = len(options) * button_size + (len(options) - 1) * spacing
    start_x = panel_x + (panel_width - total_buttons_width) // 2

    for i, opt in enumerate(options):
        rect = pygame.Rect(start_x + i * (button_size + spacing), panel_y + 40, button_size, button_size)
        buttons.append((rect, color + opt))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                for rect, piece_name in buttons:
                    if rect.collidepoint(x, y):
                        choice = piece_name[1]  # letra q/r/b/n
                        running = False

        # Dibujar botones con imágenes
        for rect, piece_name in buttons:
            pygame.draw.rect(screen, (100, 100, 100), rect, border_radius=5)  # Fondo del botón
            pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=5)  # Borde del botón
            img = IMAGES[piece_name]
            img_scaled = pygame.transform.scale(img, (rect.width, rect.height))
            screen.blit(img_scaled, rect.topleft)

        pygame.display.flip()

    return choice

def modal_game_over(screen, message, board):
    """
    Muestra un modal con el mensaje de jaque mate y opciones.
    Recibe 'board' para poder redibujar el tablero congelado de fondo.
    """
    font = pygame.font.SysFont("Arial", 36, bold=True)
    small_font = pygame.font.SysFont("Arial", 28)

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

    # Panel del modal
    panel_width = 450
    panel_height = 300
    panel_x = (WIDTH - panel_width) // 2
    panel_y = (HEIGHT - panel_height) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, (50, 50, 50), panel_rect, border_radius=15)
    pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3, border_radius=15)

    # Texto principal
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH//2, panel_y + 50))
    screen.blit(text, text_rect)

    # Botón "Jugar de nuevo"
    play_again_rect = pygame.Rect(panel_x + (panel_width - 240) // 2, panel_y + 150, 240, 50)
    pygame.draw.rect(screen, (0, 150, 0), play_again_rect, border_radius=10)  # Verde oscuro
    pygame.draw.rect(screen, (0, 200, 0), play_again_rect, 2, border_radius=10)  # Borde verde claro
    play_text = small_font.render("Jugar de nuevo", True, (255, 255, 255))
    play_text_rect = play_text.get_rect(center=play_again_rect.center)
    screen.blit(play_text, play_text_rect)

    # Botón "Salir"
    exit_rect = pygame.Rect(panel_x + (panel_width - 240) // 2, panel_y + 220, 240, 50)
    pygame.draw.rect(screen, (150, 0, 0), exit_rect, border_radius=10)  # Rojo oscuro
    pygame.draw.rect(screen, (200, 0, 0), exit_rect, 2, border_radius=10)  # Borde rojo claro
    exit_text = small_font.render("Salir", True, (255, 255, 255))
    exit_text_rect = exit_text.get_rect(center=exit_rect.center)
    screen.blit(exit_text, exit_text_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if play_again_rect.collidepoint(x, y):
                    pygame.event.clear()
                    return "play_again"
                elif exit_rect.collidepoint(x, y):
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()

def modal_choose_mode(screen):
    """
    Modal inicial: elegir jugar contra Humano o IA.
    Retorna 'human' o 'ia'.
    """
    font = pygame.font.SysFont("Arial", 36, bold=True)
    small_font = pygame.font.SysFont("Arial", 28)

    # Fondo
    screen.fill((30, 30, 30))  # Fondo oscuro para el inicio

    # Panel del modal
    panel_width = 450
    panel_height = 300
    panel_x = (WIDTH - panel_width) // 2
    panel_y = (HEIGHT - panel_height) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, (50, 50, 50), panel_rect, border_radius=15)
    pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3, border_radius=15)

    # Texto principal
    text = font.render("Elige modo de juego", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH//2, panel_y + 50))
    screen.blit(text, text_rect)

    # Botón Humano
    human_rect = pygame.Rect(panel_x + (panel_width - 280) // 2, panel_y + 130, 280, 50)
    pygame.draw.rect(screen, (0, 100, 150), human_rect, border_radius=10)  # Azul oscuro
    pygame.draw.rect(screen, (0, 150, 200), human_rect, 2, border_radius=10)  # Borde azul claro
    h_text = small_font.render("Humano vs Humano", True, (255, 255, 255))
    h_text_rect = h_text.get_rect(center=human_rect.center)
    screen.blit(h_text, h_text_rect)

    # Botón IA
    ia_rect = pygame.Rect(panel_x + (panel_width - 280) // 2, panel_y + 200, 280, 50)
    pygame.draw.rect(screen, (150, 100, 0), ia_rect, border_radius=10)  # Naranja oscuro
    pygame.draw.rect(screen, (200, 150, 0), ia_rect, 2, border_radius=10)  # Borde naranja claro
    ia_text = small_font.render("Humano vs IA", True, (255, 255, 255))
    ia_text_rect = ia_text.get_rect(center=ia_rect.center)
    screen.blit(ia_text, ia_text_rect)

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
        pygame.display.flip()

def modal_choose_difficulty(screen):
    """
    Modal para elegir dificultad de la IA: fácil (A*) o difícil (Minimax).
    Retorna 'easy' o 'hard'.
    """
    font = pygame.font.SysFont("Arial", 36, bold=True)
    small_font = pygame.font.SysFont("Arial", 28)

    # Fondo
    screen.fill((30, 30, 30))

    # Panel
    panel_width = 450
    panel_height = 250
    panel_x = (WIDTH - panel_width) // 2
    panel_y = (HEIGHT - panel_height) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, (50, 50, 50), panel_rect, border_radius=15)
    pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3, border_radius=15)

    # Texto principal
    text = font.render("Elige dificultad", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH//2, panel_y + 50))
    screen.blit(text, text_rect)

    # Botón Fácil
    easy_rect = pygame.Rect(panel_x + (panel_width - 280) // 2, panel_y + 120, 280, 50)
    pygame.draw.rect(screen, (0, 120, 0), easy_rect, border_radius=10)  # Verde oscuro
    pygame.draw.rect(screen, (0, 200, 0), easy_rect, 2, border_radius=10)  # Verde claro
    e_text = small_font.render("Fácil (A*)", True, (255, 255, 255))
    e_text_rect = e_text.get_rect(center=easy_rect.center)
    screen.blit(e_text, e_text_rect)

    # Botón Difícil
    hard_rect = pygame.Rect(panel_x + (panel_width - 280) // 2, panel_y + 190, 280, 50)
    pygame.draw.rect(screen, (120, 0, 0), hard_rect, border_radius=10)  # Rojo oscuro
    pygame.draw.rect(screen, (200, 0, 0), hard_rect, 2, border_radius=10)  # Rojo claro
    h_text = small_font.render("Difícil (Minimax)", True, (255, 255, 255))
    h_text_rect = h_text.get_rect(center=hard_rect.center)
    screen.blit(h_text, h_text_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if easy_rect.collidepoint(x, y):
                    return "easy"
                elif hard_rect.collidepoint(x, y):
                    return "hard"
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

    difficulty = None
    if mode == "ia":
        difficulty = modal_choose_difficulty(screen)  # ← 'easy' o 'hard'

    selected_square = None
    running = True
    last_turn = board.turn  # Guardamos el turno anterior

    while running:
        
        is_human_turn = mode == "human" or (mode == "ia" and board.turn == "w")

        # --- 1) Procesar eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if is_human_turn:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    col = x // SQ_SIZE
                    row = y // SQ_SIZE

                    if selected_square is None:
                        piece_at_square = board.get_piece(row, col)
                        if piece_at_square != "--" and piece_at_square[0] == board.turn:
                            selected_square = (row, col)
                    else:
                        start = selected_square
                        end = (row, col)
                        piece = board.get_piece(*start)
                        temp_move = Move(start, end, board)

                        if board.is_valid_move(start, end):
                            promote_to = None
                            if temp_move.is_pawn_promotion:
                                promote_to = promotion_menu(screen, piece[0])

                            turno_actual = board.turn
                            move = Move(start, end, board, promotion_choice=promote_to or "q")
                            board.make_move(move)

                            draw_board(screen)
                            if board.is_check(board.turn):
                                king_row, king_col = board.white_king_pos if board.turn == "w" else board.black_king_pos
                                highlight_king_in_check(screen, king_row, king_col)
                            for r_draw in range(8):
                                for c_draw in range(8):
                                    piece_draw = board.get_piece(r_draw, c_draw)
                                    if piece_draw != "--":
                                        screen.blit(IMAGES[piece_draw], (c_draw * SQ_SIZE, r_draw * SQ_SIZE))
                            pygame.display.flip()

                            

                            # Revisar fin de juego
                            if board.is_checkmate(board.turn):
                                ganador = "Blancas" if turno_actual == "w" else "Negras"
                                action = modal_game_over(screen, f"¡Jaque Mate! Ganaron las {ganador}", board)
                                if action == "play_again":
                                    board = ChessBoard()
                                    selected_square = None
                                    last_turn = board.turn
                                    mode = modal_choose_mode(screen)
                                    if mode == "ia":
                                        difficulty = modal_choose_difficulty(screen)
                                else:
                                    running = False
                            elif board.is_stalemate(board.turn):
                                action = modal_game_over(screen, "¡Ahogado! Es un empate.", board)
                                if action == "play_again":
                                    board = ChessBoard()
                                    selected_square = None
                                    last_turn = board.turn
                                    mode = modal_choose_mode(screen)
                                    if mode == "ia":
                                        difficulty = modal_choose_difficulty(screen)
                                else:
                                    running = False

                            last_turn = "w" if board.turn == "b" else "b"
                        selected_square = None

        # --- 2) Turno de la IA ---
        if mode == "ia" and board.turn == "b" and last_turn != board.turn and running:
            if difficulty == "easy":
                from IA.a_star import get_best_move_astar
                best_move = get_best_move_astar(board, depth_limit=2, beam_width=5)
            else:
                from IA.search import get_best_move
                best_move = get_best_move(board, max_depth=3, time_limit=5.0)

            if best_move:
                board.make_move(best_move)

                draw_board(screen)
                if board.is_check(board.turn):
                    king_row, king_col = board.white_king_pos if board.turn == "w" else board.black_king_pos
                    highlight_king_in_check(screen, king_row, king_col)
                for r_draw in range(8):
                    for c_draw in range(8):
                        piece_draw = board.get_piece(r_draw, c_draw)
                        if piece_draw != "--":
                            screen.blit(IMAGES[piece_draw], (c_draw * SQ_SIZE, r_draw * SQ_SIZE))
                pygame.display.flip()

                # Revisar fin de juego
                if board.is_checkmate(board.turn):
                    ganador = "Negras" if board.turn == "w" else "Blancas"
                    action = modal_game_over(screen, f"¡Jaque Mate! Ganaron las {ganador}", board)
                    if action == "play_again":
                        board = ChessBoard()
                        selected_square = None
                        last_turn = board.turn
                        mode = modal_choose_mode(screen)
                        if mode == "ia":
                            difficulty = modal_choose_difficulty(screen)
                    else:
                        running = False
                elif board.is_stalemate(board.turn):
                    action = modal_game_over(screen, "¡Ahogado! Es un empate.", board)
                    if action == "play_again":
                        board = ChessBoard()
                        selected_square = None
                        last_turn = board.turn
                        mode = modal_choose_mode(screen)
                        if mode == "ia":
                            difficulty = modal_choose_difficulty(screen)
                    else:
                        running = False

                last_turn = board.turn
            else:
                print("IA no encontró movimiento válido.")
                last_turn = board.turn

        # --- 3) Dibujar el tablero ---
        draw_board(screen)
        if board.is_check(board.turn):
            king_row, king_col = board.white_king_pos if board.turn == "w" else board.black_king_pos
            highlight_king_in_check(screen, king_row, king_col)

        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece != "--":
                    screen.blit(IMAGES[piece], (c * SQ_SIZE, r * SQ_SIZE))

        if selected_square and is_human_turn:
            highlight_square(screen, selected_square[0], selected_square[1])
            try:
                legal_moves = board.get_legal_moves(board.turn)
                for move in legal_moves:
                    if move.start_row == selected_square[0] and move.start_col == selected_square[1]:
                        highlight_square(screen, move.end_row, move.end_col)
            except AttributeError:
                pass

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_game()

