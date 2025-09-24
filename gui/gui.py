import pygame # Importa la biblioteca Pygame para el desarrollo de juegos y gráficos.
from gui.board import draw_board, highlight_square, highlight_king_in_check # Importa funciones para dibujar el tablero y resaltar casillas.
from gui.pieces import load_images, IMAGES # Importa funciones para cargar imágenes de piezas y el diccionario de imágenes.
from chessLogic.chessboard import ChessBoard # Importa la clase ChessBoard que maneja la lógica del ajedrez.
from chessLogic.move import Move # Importa la clase Move para representar los movimientos en el ajedrez.
from IA.search import get_best_move # Importa la función para obtener el mejor movimiento de la IA (Minimax).
import sys  # Importar sys para sys.exit() para salir de la aplicación.

WIDTH, HEIGHT = 640, 640 # Define el ancho y alto de la ventana del juego.
SQ_SIZE = WIDTH // 8 # Calcula el tamaño de cada casilla del tablero.

def promotion_menu(screen, color):
    """
    Muestra opciones de promoción usando imágenes y devuelve la elección del jugador.
    color: 'w' o 'b' (color de la pieza que promociona)
    """
    options = ['q', 'r', 'b', 'n']  # Opciones de promoción: reina, torre, alfil, caballo.
    running = True # Bandera para controlar el bucle del menú.
    choice = None # Variable para almacenar la elección del jugador.

    # Fondo semitransparente para el modal, para oscurecer el tablero de fondo.
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Crea una superficie con canal alfa.
    s.fill((0, 0, 0, 180))  # Rellena con negro semitransparente (180 de opacidad).
    screen.blit(s, (0, 0)) # Dibuja la superficie semitransparente en la pantalla.

    # Dibujar un panel para las opciones del menú.
    panel_width = 400 # Ancho del panel.
    panel_height = 100 # Alto del panel.
    panel_x = (WIDTH - panel_width) // 2 # Posición X para centrar el panel.
    panel_y = (HEIGHT - panel_height) // 2 # Posición Y para centrar el panel.
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height) # Crea el rectángulo del panel.
    pygame.draw.rect(screen, (50, 50, 50), panel_rect, border_radius=10)  # Dibuja el fondo oscuro del panel con bordes redondeados.
    pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3, border_radius=10)  # Dibuja un borde claro para el panel.

    font = pygame.font.SysFont("Arial", 24, bold=True) # Define la fuente para el texto.
    text_surface = font.render("Elige pieza para promocionar:", True, (255, 255, 255)) # Crea el texto.
    text_rect = text_surface.get_rect(center=(WIDTH // 2, panel_y + 20)) # Obtiene el rectángulo del texto y lo centra.
    screen.blit(text_surface, text_rect) # Dibuja el texto en la pantalla.

    # Crear botones con posición para cada opción de promoción.
    buttons = [] # Lista para almacenar los rectángulos de los botones y los nombres de las piezas.
    button_size = 60 # Tamaño de cada botón.
    spacing = 20 # Espaciado entre botones.
    total_buttons_width = len(options) * button_size + (len(options) - 1) * spacing # Ancho total ocupado por los botones.
    start_x = panel_x + (panel_width - total_buttons_width) // 2 # Posición X inicial para centrar los botones.

    for i, opt in enumerate(options): # Itera sobre las opciones de promoción.
        rect = pygame.Rect(start_x + i * (button_size + spacing), panel_y + 40, button_size, button_size) # Crea el rectángulo del botón.
        buttons.append((rect, color + opt)) # Añade el rectángulo y el nombre de la pieza al botón.

    while running: # Bucle principal del menú de promoción.
        for event in pygame.event.get(): # Procesa los eventos de Pygame.
            if event.type == pygame.QUIT: # Si el usuario cierra la ventana.
                pygame.quit() # Cierra Pygame.
                sys.exit() # Sale de la aplicación.
            elif event.type == pygame.MOUSEBUTTONDOWN: # Si se hace clic con el ratón.
                x, y = pygame.mouse.get_pos() # Obtiene las coordenadas del clic.
                for rect, piece_name in buttons: # Itera sobre los botones.
                    if rect.collidepoint(x, y): # Si el clic está dentro de un botón.
                        choice = piece_name[1]  # Almacena la letra de la pieza elegida (q/r/b/n).
                        running = False # Sale del bucle del menú.

        # Dibujar botones con imágenes.
        for rect, piece_name in buttons: # Itera sobre los botones para dibujarlos.
            pygame.draw.rect(screen, (100, 100, 100), rect, border_radius=5)  # Dibuja el fondo del botón.
            pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=5)  # Dibuja el borde del botón.
            img = IMAGES[piece_name] # Obtiene la imagen de la pieza.
            img_scaled = pygame.transform.scale(img, (rect.width, rect.height)) # Escala la imagen al tamaño del botón.
            screen.blit(img_scaled, rect.topleft) # Dibuja la imagen escalada en el botón.

        pygame.display.flip() # Actualiza la pantalla para mostrar los cambios.

    return choice # Devuelve la elección del jugador.

def modal_game_over(screen, message, board):
    """
    Muestra un modal con el mensaje de jaque mate/ahogado y opciones.
    Recibe 'board' para poder redibujar el tablero congelado de fondo.
    """
    font = pygame.font.SysFont("Arial", 36, bold=True) # Fuente para el mensaje principal.
    small_font = pygame.font.SysFont("Arial", 28) # Fuente para los botones.

    # Redibujar tablero y piezas (estado congelado) para que se vea detrás del modal.
    draw_board(screen) # Dibuja el tablero.
    for r in range(8): # Itera sobre las filas.
        for c in range(8): # Itera sobre las columnas.
            piece = board.get_piece(r, c) # Obtiene la pieza en la casilla.
            if piece != "--": # Si hay una pieza.
                screen.blit(IMAGES[piece], (c * SQ_SIZE, r * SQ_SIZE)) # Dibuja la pieza.

    # Fondo semi-transparente encima del tablero.
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Crea una superficie con canal alfa.
    s.fill((0, 0, 0, 180)) # Rellena con negro semitransparente.
    screen.blit(s, (0, 0)) # Dibuja la superficie semitransparente.

    # Panel del modal.
    panel_width = 450 # Ancho del panel.
    panel_height = 300 # Alto del panel.
    panel_x = (WIDTH - panel_width) // 2 # Posición X para centrar el panel.
    panel_y = (HEIGHT - panel_height) // 2 # Posición Y para centrar el panel.
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height) # Crea el rectángulo del panel.
    pygame.draw.rect(screen, (50, 50, 50), panel_rect, border_radius=15) # Dibuja el fondo oscuro del panel.
    pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3, border_radius=15) # Dibuja el borde claro del panel.

    # Texto principal del mensaje de fin de juego.
    text = font.render(message, True, (255, 255, 255)) # Crea el texto del mensaje.
    text_rect = text.get_rect(center=(WIDTH//2, panel_y + 50)) # Obtiene el rectángulo del texto y lo centra.
    screen.blit(text, text_rect) # Dibuja el texto.

    # Botón "Jugar de nuevo".
    play_again_rect = pygame.Rect(panel_x + (panel_width - 240) // 2, panel_y + 150, 240, 50) # Crea el rectángulo del botón.
    pygame.draw.rect(screen, (0, 150, 0), play_again_rect, border_radius=10)  # Dibuja el fondo verde oscuro del botón.
    pygame.draw.rect(screen, (0, 200, 0), play_again_rect, 2, border_radius=10)  # Dibuja el borde verde claro del botón.
    play_text = small_font.render("Jugar de nuevo", True, (255, 255, 255)) # Crea el texto del botón.
    play_text_rect = play_text.get_rect(center=play_again_rect.center) # Centra el texto en el botón.
    screen.blit(play_text, play_text_rect) # Dibuja el texto.

    # Botón "Salir".
    exit_rect = pygame.Rect(panel_x + (panel_width - 240) // 2, panel_y + 220, 240, 50) # Crea el rectángulo del botón.
    pygame.draw.rect(screen, (150, 0, 0), exit_rect, border_radius=10)  # Dibuja el fondo rojo oscuro del botón.
    pygame.draw.rect(screen, (200, 0, 0), exit_rect, 2, border_radius=10)  # Dibuja el borde rojo claro del botón.
    exit_text = small_font.render("Salir", True, (255, 255, 255)) # Crea el texto del botón.
    exit_text_rect = exit_text.get_rect(center=exit_rect.center) # Centra el texto en el botón.
    screen.blit(exit_text, exit_text_rect) # Dibuja el texto.

    while True: # Bucle principal del modal de fin de juego.
        for event in pygame.event.get(): # Procesa los eventos de Pygame.
            if event.type == pygame.QUIT: # Si el usuario cierra la ventana.
                pygame.quit() # Cierra Pygame.
                sys.exit() # Sale de la aplicación.
            elif event.type == pygame.MOUSEBUTTONDOWN: # Si se hace clic con el ratón.
                x, y = pygame.mouse.get_pos() # Obtiene las coordenadas del clic.
                if play_again_rect.collidepoint(x, y): # Si el clic está en el botón "Jugar de nuevo".
                    pygame.event.clear() # Limpia la cola de eventos.
                    return "play_again" # Retorna para reiniciar el juego.
                elif exit_rect.collidepoint(x, y): # Si el clic está en el botón "Salir".
                    pygame.quit() # Cierra Pygame.
                    sys.exit() # Sale de la aplicación.
        pygame.display.flip() # Actualiza la pantalla.

def modal_choose_mode(screen):
    """
    Modal inicial: elegir jugar contra Humano o IA.
    Retorna 'human' o 'ia'.
    """
    font = pygame.font.SysFont("Arial", 36, bold=True) # Fuente para el mensaje principal.
    small_font = pygame.font.SysFont("Arial", 28) # Fuente para los botones.

    # Fondo del modal.
    screen.fill((30, 30, 30))  # Rellena la pantalla con un color oscuro.

    # Panel del modal.
    panel_width = 450 # Ancho del panel.
    panel_height = 300 # Alto del panel.
    panel_x = (WIDTH - panel_width) // 2 # Posición X para centrar el panel.
    panel_y = (HEIGHT - panel_height) // 2 # Posición Y para centrar el panel.
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height) # Crea el rectángulo del panel.
    pygame.draw.rect(screen, (50, 50, 50), panel_rect, border_radius=15) # Dibuja el fondo oscuro del panel.
    pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3, border_radius=15) # Dibuja el borde claro del panel.

    # Texto principal.
    text = font.render("Elige modo de juego", True, (255, 255, 255)) # Crea el texto.
    text_rect = text.get_rect(center=(WIDTH//2, panel_y + 50)) # Centra el texto.
    screen.blit(text, text_rect) # Dibuja el texto.

    # Botón Humano vs Humano.
    human_rect = pygame.Rect(panel_x + (panel_width - 280) // 2, panel_y + 130, 280, 50) # Crea el rectángulo del botón.
    pygame.draw.rect(screen, (0, 100, 150), human_rect, border_radius=10)  # Dibuja el fondo azul oscuro.
    pygame.draw.rect(screen, (0, 150, 200), human_rect, 2, border_radius=10)  # Dibuja el borde azul claro.
    h_text = small_font.render("Humano vs Humano", True, (255, 255, 255)) # Crea el texto.
    h_text_rect = h_text.get_rect(center=human_rect.center) # Centra el texto.
    screen.blit(h_text, h_text_rect) # Dibuja el texto.

    # Botón Humano vs IA.
    ia_rect = pygame.Rect(panel_x + (panel_width - 280) // 2, panel_y + 200, 280, 50) # Crea el rectángulo del botón.
    pygame.draw.rect(screen, (150, 100, 0), ia_rect, border_radius=10)  # Dibuja el fondo naranja oscuro.
    pygame.draw.rect(screen, (200, 150, 0), ia_rect, 2, border_radius=10)  # Dibuja el borde naranja claro.
    ia_text = small_font.render("Humano vs IA", True, (255, 255, 255)) # Crea el texto.
    ia_text_rect = ia_text.get_rect(center=ia_rect.center) # Centra el texto.
    screen.blit(ia_text, ia_text_rect) # Dibuja el texto.

    while True: # Bucle principal del modal de elección de modo.
        for event in pygame.event.get(): # Procesa los eventos de Pygame.
            if event.type == pygame.QUIT: # Si el usuario cierra la ventana.
                pygame.quit() # Cierra Pygame.
                sys.exit() # Sale de la aplicación.
            elif event.type == pygame.MOUSEBUTTONDOWN: # Si se hace clic con el ratón.
                x, y = pygame.mouse.get_pos() # Obtiene las coordenadas del clic.
                if human_rect.collidepoint(x, y): # Si el clic está en el botón "Humano vs Humano".
                    return "human" # Retorna "human".
                elif ia_rect.collidepoint(x, y): # Si el clic está en el botón "Humano vs IA".
                    return "ia" # Retorna "ia".
        pygame.display.flip() # Actualiza la pantalla.

def modal_choose_difficulty(screen):
    """
    Modal para elegir dificultad de la IA: fácil (A*) o difícil (Minimax).
    Retorna 'easy' o 'hard'.
    """
    font = pygame.font.SysFont("Arial", 36, bold=True) # Fuente para el mensaje principal.
    small_font = pygame.font.SysFont("Arial", 28) # Fuente para los botones.

    # Fondo del modal.
    screen.fill((30, 30, 30)) # Rellena la pantalla con un color oscuro.

    # Panel del modal.
    panel_width = 450 # Ancho del panel.
    panel_height = 250 # Alto del panel.
    panel_x = (WIDTH - panel_width) // 2 # Posición X para centrar el panel.
    panel_y = (HEIGHT - panel_height) // 2 # Posición Y para centrar el panel.
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height) # Crea el rectángulo del panel.
    pygame.draw.rect(screen, (50, 50, 50), panel_rect, border_radius=15) # Dibuja el fondo oscuro del panel.
    pygame.draw.rect(screen, (200, 200, 200), panel_rect, 3, border_radius=15) # Dibuja el borde claro del panel.

    # Texto principal.
    text = font.render("Elige dificultad", True, (255, 255, 255)) # Crea el texto.
    text_rect = text.get_rect(center=(WIDTH//2, panel_y + 50)) # Centra el texto.
    screen.blit(text, text_rect) # Dibuja el texto.

    # Botón Fácil (A*).
    easy_rect = pygame.Rect(panel_x + (panel_width - 280) // 2, panel_y + 120, 280, 50) # Crea el rectángulo del botón.
    pygame.draw.rect(screen, (0, 120, 0), easy_rect, border_radius=10)  # Dibuja el fondo verde oscuro.
    pygame.draw.rect(screen, (0, 200, 0), easy_rect, 2, border_radius=10)  # Dibuja el borde verde claro.
    e_text = small_font.render("Fácil (A*)", True, (255, 255, 255)) # Crea el texto.
    e_text_rect = e_text.get_rect(center=easy_rect.center) # Centra el texto.
    screen.blit(e_text, e_text_rect) # Dibuja el texto.

    # Botón Difícil (Minimax).
    hard_rect = pygame.Rect(panel_x + (panel_width - 280) // 2, panel_y + 190, 280, 50) # Crea el rectángulo del botón.
    pygame.draw.rect(screen, (120, 0, 0), hard_rect, border_radius=10)  # Dibuja el fondo rojo oscuro.
    pygame.draw.rect(screen, (200, 0, 0), hard_rect, 2, border_radius=10)  # Dibuja el borde rojo claro.
    h_text = small_font.render("Difícil (Minimax)", True, (255, 255, 255)) # Crea el texto.
    h_text_rect = h_text.get_rect(center=hard_rect.center) # Centra el texto.
    screen.blit(h_text, h_text_rect) # Dibuja el texto.

    while True: # Bucle principal del modal de elección de dificultad.
        for event in pygame.event.get(): # Procesa los eventos de Pygame.
            if event.type == pygame.QUIT: # Si el usuario cierra la ventana.
                pygame.quit() # Cierra Pygame.
                sys.exit() # Sale de la aplicación.
            elif event.type == pygame.MOUSEBUTTONDOWN: # Si se hace clic con el ratón.
                x, y = pygame.mouse.get_pos() # Obtiene las coordenadas del clic.
                if easy_rect.collidepoint(x, y): # Si el clic está en el botón "Fácil".
                    return "easy" # Retorna "easy".
                elif hard_rect.collidepoint(x, y): # Si el clic está en el botón "Difícil".
                    return "hard" # Retorna "hard".
        pygame.display.flip() # Actualiza la pantalla.


def run_game():
    pygame.init() # Inicializa todos los módulos de Pygame.
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) # Crea la ventana del juego.
    pygame.display.set_caption("Ajedrez con IA: PHIA") # Establece el título de la ventana.

    clock = pygame.time.Clock() # Crea un objeto Clock para controlar la velocidad del juego.
    board = ChessBoard() # Crea una nueva instancia del tablero de ajedrez.
    load_images() # Carga todas las imágenes de las piezas.

    # 🔹 Preguntar modo antes de iniciar el juego.
    mode = modal_choose_mode(screen)  # Llama al modal para elegir entre 'ia' o 'human'.

    difficulty = None # Inicializa la dificultad como None.
    if mode == "ia": # Si el modo de juego es contra la IA.
        difficulty = modal_choose_difficulty(screen)  # Llama al modal para elegir entre 'easy' o 'hard'.

    selected_square = None # Almacena la casilla seleccionada por el jugador.
    running = True # Bandera para controlar el bucle principal del juego.
    last_turn = board.turn  # Guarda el turno anterior para detectar cambios.

    while running: # Bucle principal del juego.
        
        # Determina si es el turno del jugador humano.
        is_human_turn = mode == "human" or (mode == "ia" and board.turn == "w")

        # --- 1) Procesar eventos ---
        for event in pygame.event.get(): # Itera sobre todos los eventos de Pygame.
            if event.type == pygame.QUIT: # Si el usuario cierra la ventana.
                running = False # Establece la bandera a False para salir del bucle.

            if is_human_turn: # Si es el turno del jugador humano.
                if event.type == pygame.MOUSEBUTTONDOWN: # Si se hace clic con el ratón.
                    x, y = pygame.mouse.get_pos() # Obtiene las coordenadas del clic.
                    col = x // SQ_SIZE # Calcula la columna de la casilla clicada.
                    row = y // SQ_SIZE # Calcula la fila de la casilla clicada.

                    if selected_square is None: # Si no hay ninguna casilla seleccionada.
                        piece_at_square = board.get_piece(row, col) # Obtiene la pieza en la casilla clicada.
                        # Si hay una pieza y es del color del turno actual.
                        if piece_at_square != "--" and piece_at_square[0] == board.turn:
                            selected_square = (row, col) # Selecciona esta casilla.
                    else: # Si ya hay una casilla seleccionada.
                        start = selected_square # La casilla seleccionada es el inicio del movimiento.
                        end = (row, col) # La casilla clicada es el final del movimiento.
                        piece = board.get_piece(*start) # Obtiene la pieza que se va a mover.
                        temp_move = Move(start, end, board) # Crea un movimiento temporal para verificar promoción.

                        if board.is_valid_move(start, end): # Si el movimiento es válido.
                            promote_to = None # Inicializa la elección de promoción.
                            if temp_move.is_pawn_promotion: # Si el movimiento es una promoción de peón.
                                promote_to = promotion_menu(screen, piece[0]) # Muestra el menú de promoción.

                            turno_actual = board.turn # Guarda el turno actual antes de hacer el movimiento.
                            move = Move(start, end, board, promotion_choice=promote_to or "q") # Crea el objeto Move.
                            board.make_move(move) # Realiza el movimiento en el tablero.

                            draw_board(screen) # Redibuja el tablero.
                            if board.is_check(board.turn): # Si el rey del turno actual está en jaque.
                                king_row, king_col = board.white_king_pos if board.turn == "w" else board.black_king_pos # Obtiene la posición del rey.
                                highlight_king_in_check(screen, king_row, king_col) # Resalta el rey en jaque.
                            for r_draw in range(8): # Itera para dibujar todas las piezas.
                                for c_draw in range(8):
                                    piece_draw = board.get_piece(r_draw, c_draw)
                                    if piece_draw != "--":
                                        screen.blit(IMAGES[piece_draw], (c_draw * SQ_SIZE, r_draw * SQ_SIZE))
                            pygame.display.flip() # Actualiza la pantalla.

                            # Revisar fin de juego (jaque mate o ahogado).
                            if board.is_checkmate(board.turn): # Si es jaque mate.
                                ganador = "Blancas" if turno_actual == "w" else "Negras" # Determina el ganador.
                                action = modal_game_over(screen, f"¡Jaque Mate! Ganaron las {ganador}", board) # Muestra el modal de fin de juego.
                                if action == "play_again": # Si el jugador elige jugar de nuevo.
                                    board = ChessBoard() # Reinicia el tablero.
                                    selected_square = None # Deselecciona la casilla.
                                    last_turn = board.turn # Reinicia el turno anterior.
                                    mode = modal_choose_mode(screen) # Vuelve a preguntar el modo de juego.
                                    if mode == "ia": # Si es contra IA, pregunta la dificultad.
                                        difficulty = modal_choose_difficulty(screen)
                                else:
                                    running = False # Si no, sale del juego.
                            elif board.is_stalemate(board.turn): # Si es ahogado.
                                action = modal_game_over(screen, "¡Ahogado! Es un empate.", board) # Muestra el modal de fin de juego.
                                if action == "play_again": # Si el jugador elige jugar de nuevo.
                                    board = ChessBoard() # Reinicia el tablero.
                                    selected_square = None # Deselecciona la casilla.
                                    last_turn = board.turn # Reinicia el turno anterior.
                                    mode = modal_choose_mode(screen) # Vuelve a preguntar el modo de juego.
                                    if mode == "ia": # Si es contra IA, pregunta la dificultad.
                                        difficulty = modal_choose_difficulty(screen)
                                else:
                                    running = False # Si no, sale del juego.

                            last_turn = "w" if board.turn == "b" else "b" # Actualiza el turno anterior.
                        selected_square = None # Deselecciona la casilla después del movimiento.

        # --- 2) Turno de la IA ---
        # Si el modo es IA, es el turno de las negras (IA), y el turno ha cambiado, y el juego sigue.
        if mode == "ia" and board.turn == "b" and last_turn != board.turn and running:
            if difficulty == "easy": # Si la dificultad es fácil.
                from IA.a_star import get_best_move_astar # Importa el algoritmo A*.
                best_move = get_best_move_astar(board, depth_limit=2, beam_width=5) # Obtiene el mejor movimiento con A*.
            else: # Si la dificultad es difícil.
                from IA.search import get_best_move # Importa el algoritmo Minimax.
                best_move = get_best_move(board, max_depth=3, time_limit=5.0) # Obtiene el mejor movimiento con Minimax.

            if best_move: # Si la IA encontró un movimiento.
                board.make_move(best_move) # Realiza el movimiento de la IA.

                draw_board(screen) # Redibuja el tablero.
                if board.is_check(board.turn): # Si el rey del turno actual está en jaque.
                    king_row, king_col = board.white_king_pos if board.turn == "w" else board.black_king_pos # Obtiene la posición del rey.
                    highlight_king_in_check(screen, king_row, king_col) # Resalta el rey en jaque.
                for r_draw in range(8): # Itera para dibujar todas las piezas.
                    for c_draw in range(8):
                        piece_draw = board.get_piece(r_draw, c_draw)
                        if piece_draw != "--":
                            screen.blit(IMAGES[piece_draw], (c_draw * SQ_SIZE, r_draw * SQ_SIZE))
                pygame.display.flip() # Actualiza la pantalla.

                # Revisar fin de juego (jaque mate o ahogado).
                if board.is_checkmate(board.turn): # Si es jaque mate.
                    ganador = "Negras" if board.turn == "w" else "Blancas" # Determina el ganador.
                    action = modal_game_over(screen, f"¡Jaque Mate! Ganaron las {ganador}", board) # Muestra el modal de fin de juego.
                    if action == "play_again": # Si el jugador elige jugar de nuevo.
                        board = ChessBoard() # Reinicia el tablero.
                        selected_square = None # Deselecciona la casilla.
                        last_turn = board.turn # Reinicia el turno anterior.
                        mode = modal_choose_mode(screen) # Vuelve a preguntar el modo de juego.
                        if mode == "ia": # Si es contra IA, pregunta la dificultad.
                            difficulty = modal_choose_difficulty(screen)
                    else:
                        running = False # Si no, sale del juego.
                elif board.is_stalemate(board.turn): # Si es ahogado.
                    action = modal_game_over(screen, "¡Ahogado! Es un empate.", board) # Muestra el modal de fin de juego.
                    if action == "play_again": # Si el jugador elige jugar de nuevo.
                        board = ChessBoard() # Reinicia el tablero.
                        selected_square = None # Deselecciona la casilla.
                        last_turn = board.turn # Reinicia el turno anterior.
                        mode = modal_choose_mode(screen) # Vuelve a preguntar el modo de juego.
                        if mode == "ia": # Si es contra IA, pregunta la dificultad.
                            difficulty = modal_choose_difficulty(screen)
                    else:
                        running = False # Si no, sale del juego.

                last_turn = board.turn # Actualiza el turno anterior.
            else:
                print("IA no encontró movimiento válido.") # Mensaje si la IA no encuentra movimiento.
                last_turn = board.turn # Mantiene el turno anterior para evitar bucles.

        # --- 3) Dibujar el tablero ---
        draw_board(screen) # Dibuja el tablero.
        if board.is_check(board.turn): # Si el rey del turno actual está en jaque.
            king_row, king_col = board.white_king_pos if board.turn == "w" else board.black_king_pos # Obtiene la posición del rey.
            highlight_king_in_check(screen, king_row, king_col) # Resalta el rey en jaque.

        for r in range(8): # Itera sobre las filas.
            for c in range(8): # Itera sobre las columnas.
                piece = board.get_piece(r, c) # Obtiene la pieza en la casilla.
                if piece != "--": # Si hay una pieza.
                    screen.blit(IMAGES[piece], (c * SQ_SIZE, r * SQ_SIZE)) # Dibuja la pieza.

        if selected_square and is_human_turn: # Si hay una casilla seleccionada y es el turno humano.
            highlight_square(screen, selected_square[0], selected_square[1]) # Resalta la casilla seleccionada.
            try:
                legal_moves = board.get_legal_moves(board.turn) # Obtiene los movimientos legales para el turno actual.
                for move in legal_moves: # Itera sobre los movimientos legales.
                    # Si el movimiento comienza desde la casilla seleccionada.
                    if move.start_row == selected_square[0] and move.start_col == selected_square[1]:
                        highlight_square(screen, move.end_row, move.end_col) # Resalta las casillas de destino posibles.
            except AttributeError: # Maneja posibles errores si move no tiene atributos de fila/columna.
                pass

        pygame.display.flip() # Actualiza la pantalla para mostrar todos los elementos dibujados.
        clock.tick(60) # Limita el bucle a 60 fotogramas por segundo.

    pygame.quit() # Desinicializa Pygame.
    sys.exit() # Sale de la aplicación.


if __name__ == "__main__":
    run_game() # Ejecuta la función principal del juego si el script se ejecuta directamente.



