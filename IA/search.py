# IA/search.py
import time # Importa el módulo time para medir el tiempo de ejecución.
from IA.evaluation import evaluate_board, piece_values # Importa la función de evaluación y los valores de las piezas.
from IA.move_generator import MoveGenerator # Importa la clase MoveGenerator para obtener movimientos.
from chessLogic.move import Move as MoveClass # Importa la clase Move (renombrada para evitar conflictos).
from chessLogic.rules import ChessRules # Importa ChessRules para verificar jaques y enroques.

MATE_SCORE = 1000000 # Puntuación muy alta para jaque mate, asegurando que siempre sea la mejor opción.
STALEMATE_SCORE = 0 # Puntuación para ahogado (empate).

# Tabla de transposiciones (simple diccionario para almacenar resultados de posiciones ya evaluadas).
transposition_table = {}

# Killer moves y history heuristic para mejorar el ordenamiento de movimientos.
killer_moves = {}       # killer_moves[depth] = [move1, move2] - Almacena movimientos que causaron podas beta.
history_heuristic = {}  # history_heuristic[(piece, end)] = score - Almacena la "bondad" histórica de un movimiento.

# --- Move ordering mejorado ---
def order_moves(board, moves, depth):
    """
    Ordena una lista de movimientos para mejorar la eficiencia de la poda alfa-beta.
    Prioriza capturas, promociones, killer moves y movimientos con buen historial.
    
    Args:
        board (ChessBoard): La instancia actual del tablero de ajedrez.
        moves (list): Lista de movimientos a ordenar (tuplas (start, end)).
        depth (int): La profundidad actual de la búsqueda.
        
    Returns:
        list: La lista de movimientos ordenada.
    """
    def move_priority(m):
        """
        Función interna para calcular la prioridad de un movimiento.
        """
        start, end = m # Desempaqueta el movimiento.
        piece = board.get_piece(*start) # Pieza que se mueve.
        target = board.get_piece(*end) # Pieza en la casilla de destino.
        score = 0 # Puntuación de prioridad del movimiento.

        # Capturas valiosas (MVV-LVA: Most Valuable Victim - Least Valuable Attacker).
        # Prioriza capturar piezas de alto valor con piezas de bajo valor.
        if target != "--": # Si es una captura.
            # 10 * valor_pieza_capturada - valor_pieza_atacante.
            score += 10 * piece_values.get(target[1], 0) - piece_values.get(piece[1], 0)

        # Promoción de peón.
        if piece[1] == "p" and (end[0] == 0 or end[0] == 7): # Si es un peón que llega a la última fila.
            score += 900 # Bonificación alta, equivalente al valor de una reina.

        # Killer moves (movimientos que causaron podas en otras ramas de búsqueda).
        if depth in killer_moves:
            for km in killer_moves[depth]:
                if m == km:
                    score += 800 # Alta prioridad para killer moves.
                    break

        # History heuristic (movimientos que han sido buenos en el pasado).
        score += history_heuristic.get((piece, end), 0) # Añade la puntuación histórica.

        return -score # Retorna el negativo para ordenar de mayor a menor prioridad (heapq es min-heap).

    return sorted(moves, key=move_priority) # Ordena la lista de movimientos usando la función de prioridad.

# --- Quiescence Search ---
def quiescence_search(board, alpha, beta, is_maximizing):
    """
    Búsqueda de quiescencia para manejar el "horizonte" del algoritmo Minimax.
    Extiende la búsqueda en posiciones donde hay movimientos "tácticos" (capturas, promociones)
    para evitar el problema del horizonte.
    
    Args:
        board (ChessBoard): La instancia actual del tablero de ajedrez.
        alpha (float): El valor alfa para la poda alfa-beta.
        beta (float): El valor beta para la poda alfa-beta.
        is_maximizing (bool): True si es el turno del jugador maximizador, False si es el minimizador.
        
    Returns:
        float: La puntuación de evaluación de la posición después de la búsqueda de quiescencia.
    """
    # Evaluar la posición actual (stand-pat): es la evaluación si no se realizan más movimientos tácticos.
    stand_pat = evaluate_board(board)

    if is_maximizing:
        if stand_pat >= beta: # Si la evaluación actual ya es mejor que beta, se puede podar.
            return beta
        alpha = max(alpha, stand_pat) # Actualiza alfa.
    else: # is_minimizing
        if stand_pat <= alpha: # Si la evaluación actual ya es peor que alfa, se puede podar.
            return alpha
        beta = min(beta, stand_pat) # Actualiza beta.

    # Generar solo movimientos "ruidosos" (capturas y promociones).
    noisy_moves = []
    all_pseudo_moves = MoveGenerator.generate_pseudo_legal_moves(board, board.turn) # Obtiene todos los pseudo-legales.
    for start, end in all_pseudo_moves:
        piece = board.get_piece(*start)
        target = board.get_piece(*end)
        # Es una captura o una promoción de peón.
        if target != "--" or (piece[1] == "p" and (end[0] == 0 or end[0] == 7)):
            noisy_moves.append((start, end))

    # Ordenar movimientos ruidosos para una poda más eficiente.
    noisy_moves = order_moves(board, noisy_moves, 0) # depth 0 para quiescence (no se usan killer/history específicos de profundidad).

    for start, end in noisy_moves:
        # Crear un objeto Move para el movimiento actual.
        m = MoveClass(start, end, board, promotion_choice="q") # Asumimos promoción a reina por defecto en búsqueda.

        # Verificar si el movimiento es legal antes de hacerlo.
        # Esto es crucial porque generate_pseudo_legal_moves no filtra jaques.
        board.make_move(m)
        # Si el rey del jugador actual está en jaque después de mover, el movimiento es ilegal.
        if ChessRules.is_in_check(board, board.turn == "w" and "b" or "w"): 
            board.undo_move()
            continue # Este movimiento es ilegal, saltar al siguiente.

        if is_maximizing:
            eval_score = quiescence_search(board, alpha, beta, False) # Llamada recursiva para el minimizador.
            board.undo_move()
            if eval_score >= beta: # Poda beta.
                return beta
            alpha = max(alpha, eval_score) # Actualiza alfa.
        else: # is_minimizing
            eval_score = quiescence_search(board, alpha, beta, True) # Llamada recursiva para el maximizador.
            board.undo_move()
            if eval_score <= alpha: # Poda alfa.
                return alpha
            beta = min(beta, eval_score) # Actualiza beta.

    return alpha if is_maximizing else beta # Devuelve el valor final de alfa o beta.

# --- Minimax con poda, transposiciones, killer/history y LMR ---
def minimax(board, depth, alpha, beta, is_maximizing):
    """
    Implementación del algoritmo Minimax con poda Alfa-Beta, tabla de transposiciones,
    killer moves, history heuristic y Late Move Reductions (LMR).
    
    Args:
        board (ChessBoard): La instancia actual del tablero de ajedrez.
        depth (int): La profundidad restante de la búsqueda.
        alpha (float): El valor alfa para la poda alfa-beta.
        beta (float): El valor beta para la poda alfa-beta.
        is_maximizing (bool): True si es el turno del jugador maximizador, False si es el minimizador.
        
    Returns:
        tuple: Una tupla (score, best_move), donde score es la evaluación de la posición
               y best_move es el mejor movimiento encontrado para llegar a esa evaluación.
    """
    # Generar un hash único para la posición actual del tablero.
    # Incluye el tablero, el turno, la casilla en passant y los derechos de enroque para una clave única.
    board_hash = hash(str(board.board) + board.turn + str(board.en_passant_square) + str(board.castling_rights))

    # Consultar la tabla de transposiciones.
    if board_hash in transposition_table:
        entry = transposition_table[board_hash]
        if entry['depth'] >= depth: # Si la entrada es lo suficientemente profunda.
            if entry['type'] == 'exact': # Si es una evaluación exacta.
                return entry['score'], entry['best_move']
            if entry['type'] == 'lowerbound' and entry['score'] > alpha: # Si es un límite inferior y mejora alfa.
                alpha = entry['score']
            if entry['type'] == 'upperbound' and entry['score'] < beta: # Si es un límite superior y mejora beta.
                beta = entry['score']
            if alpha >= beta: # Poda por tabla de transposiciones (si los límites se cruzan).
                return entry['score'], entry['best_move']

    # Caso base: profundidad 0, llamar a quiescence search para evaluar la posición.
    if depth == 0:
        score = quiescence_search(board, alpha, beta, is_maximizing)
        # Guardar en la tabla de transposiciones.
        transposition_table[board_hash] = {'score': score, 'depth': depth, 'type': 'exact', 'best_move': None}
        return score, None

    # Generar movimientos legales para el turno actual.
    moves = MoveGenerator.generate_legal_moves(board, board.turn)
    
    # Si no hay movimientos legales (jaque mate o ahogado).
    if not moves:
        if ChessRules.is_in_check(board, board.turn):
            # Jaque mate: el jugador actual pierde.
            score = (-MATE_SCORE if board.turn == "w" else MATE_SCORE)
        else:
            # Ahogado: empate.
            score = STALEMATE_SCORE
        # Guardar en la tabla de transposiciones.
        transposition_table[board_hash] = {'score': score, 'depth': depth, 'type': 'exact', 'best_move': None}
        return score, None

    # Ordenar movimientos para una poda alfa-beta más eficiente.
    moves = order_moves(board, moves, depth)
    
    best_move = None # Variable para almacenar el mejor movimiento en esta rama.
    original_alpha = alpha # Guardar alpha original para determinar el tipo de entrada en la TT.
    entry_type = 'upperbound' # Por defecto, si no se poda, es un upperbound.

    if is_maximizing: # Turno del jugador maximizador (blancas).
        max_eval = float('-inf') # Inicializa la mejor evaluación como menos infinito.
        for i, (start, end) in enumerate(moves):
            m = MoveClass(start, end, board, promotion_choice="q") # Crea el objeto Move.
            board.make_move(m) # Realiza el movimiento.

            # Late Move Reductions (LMR).
            # Reduce la profundidad de búsqueda para movimientos que no son capturas
            # y que se encuentran más tarde en la lista de movimientos ordenados.
            new_depth = depth - 1
            if depth >= 3 and i >= 4 and m.piece_captured == "--": # Ajustar umbrales de profundidad e índice.
                new_depth -= 1 # Reduce la profundidad en 1.
                if new_depth < 0: new_depth = 0 # Asegura que no sea negativo.

            eval_score, _ = minimax(board, new_depth, alpha, beta, False) # Llamada recursiva para el minimizador.
            board.undo_move() # Deshace el movimiento.

            if eval_score > max_eval: # Si se encuentra una mejor evaluación.
                max_eval = eval_score
                best_move = (start, end)

            alpha = max(alpha, eval_score) # Actualiza alfa.
            if beta <= alpha: # Poda beta: si la mejor jugada del maximizador es peor que la mejor jugada del minimizador.
                # Actualizar Killer Moves: almacena movimientos que causaron una poda beta.
                if depth not in killer_moves:
                    killer_moves[depth] = []
                if (start, end) not in killer_moves[depth]:
                    killer_moves[depth].append((start, end))
                    if len(killer_moves[depth]) > 2: # Mantener solo los 2 mejores killer moves.
                        killer_moves[depth].pop(0)
                # Actualizar History Heuristic: incrementa la puntuación del movimiento.
                piece = board.get_piece(*start)
                history_heuristic[(piece, end)] = history_heuristic.get((piece, end), 0) + depth * depth
                entry_type = 'lowerbound' # Se encontró un límite inferior.
                break # Poda.

        # Guardar en la tabla de transposiciones.
        if max_eval >= original_alpha:
            entry_type = 'exact' if max_eval < beta else 'lowerbound'
        transposition_table[board_hash] = {'score': max_eval, 'depth': depth, 'type': entry_type, 'best_move': best_move}
        return max_eval, best_move
    else: # is_minimizing (Turno del jugador minimizador - negras).
        min_eval = float('inf') # Inicializa la mejor evaluación como infinito.
        for i, (start, end) in enumerate(moves):
            m = MoveClass(start, end, board, promotion_choice="q") # Crea el objeto Move.
            board.make_move(m) # Realiza el movimiento.

            # Late Move Reductions (LMR).
            new_depth = depth - 1
            if depth >= 3 and i >= 4 and m.piece_captured == "--": # Ajustar umbrales.
                new_depth -= 1
                if new_depth < 0: new_depth = 0

            eval_score, _ = minimax(board, new_depth, alpha, beta, True) # Llamada recursiva para el maximizador.
            board.undo_move() # Deshace el movimiento.

            if eval_score < min_eval: # Si se encuentra una mejor evaluación (más baja).
                min_eval = eval_score
                best_move = (start, end)

            beta = min(beta, eval_score) # Actualiza beta.
            if beta <= alpha: # Poda alfa: si la mejor jugada del minimizador es mejor que la mejor jugada del maximizador.
                # Actualizar Killer Moves.
                if depth not in killer_moves:
                    killer_moves[depth] = []
                if (start, end) not in killer_moves[depth]:
                    killer_moves[depth].append((start, end))
                    if len(killer_moves[depth]) > 2:
                        killer_moves[depth].pop(0)
                # Actualizar History Heuristic.
                piece = board.get_piece(*start)
                history_heuristic[(piece, end)] = history_heuristic.get((piece, end), 0) + depth * depth
                entry_type = 'upperbound' # Se encontró un límite superior.
                break # Poda.

        # Guardar en la tabla de transposiciones.
        if min_eval <= original_alpha:
            entry_type = 'exact' if min_eval > alpha else 'upperbound'
        transposition_table[board_hash] = {'score': min_eval, 'depth': depth, 'type': entry_type, 'best_move': best_move}
        return min_eval, best_move

# --- Profundización iterativa ---
def get_best_move(board, max_depth=3, time_limit=10.0):
    """
    Función principal para obtener el mejor movimiento de la IA utilizando profundización iterativa.
    Realiza búsquedas Minimax a profundidades crecientes hasta alcanzar un límite de tiempo o profundidad.
    
    Args:
        board (ChessBoard): La instancia actual del tablero de ajedrez.
        max_depth (int, optional): La profundidad máxima a la que se buscará. Por defecto es 3.
        time_limit (float, optional): El límite de tiempo en segundos para la búsqueda. Por defecto es 10.0.
        
    Returns:
        MoveClass: El mejor movimiento encontrado por la IA.
    """
    start_time = time.time() # Marca el tiempo de inicio de la búsqueda.
    best_move_tuple = None # Almacena el mejor movimiento encontrado hasta ahora (como tupla).
    is_maximizing = (board.turn == "w") # Determina si el jugador actual es el maximizador.

    # Reiniciar tablas para cada nueva búsqueda (importante para evitar información obsoleta).
    global transposition_table, killer_moves, history_heuristic
    transposition_table = {} # Reinicia la tabla de transposiciones.
    killer_moves = {d: [] for d in range(max_depth + 1)} # Inicializa killer moves para cada profundidad.
    history_heuristic = {} # Reinicia la heurística de historial.

    # Iterative Deepening (Profundización Iterativa).
    for depth in range(1, max_depth + 1): # Itera desde profundidad 1 hasta max_depth.
        # Verificar límite de tiempo.
        if time.time() - start_time > time_limit:
            print(f"⏳ Tiempo límite alcanzado en profundidad {depth-1}. Usando el mejor movimiento encontrado hasta ahora.")
            break # Sale del bucle si se excede el tiempo.

        # Llamar a minimax para la profundidad actual.
        eval_score, move_tuple = minimax(board, depth, float('-inf'), float('inf'), is_maximizing)
        
        # Si se encontró un movimiento válido, actualizar el mejor movimiento global.
        if move_tuple:
            best_move_tuple = move_tuple
            # print(f"Profundidad {depth}: Mejor movimiento {move_tuple}, Evaluación: {eval_score}") # Para depuración.
        else:
            # Si no se encontró un movimiento en esta profundidad, y no hay un best_move_tuple previo,
            # significa que no hay movimientos legales o algo salió mal.
            # Esto debería ser manejado por la lógica de jaque mate/ahogado en minimax.
            pass

    # Fallback si no se encontró ningún movimiento (ej. al inicio del juego o si el tiempo se agota muy rápido).
    if not best_move_tuple:
        legal_moves = MoveGenerator.generate_legal_moves(board, board.turn) # Obtiene movimientos legales.
        if legal_moves:
            print("⚠️ No se encontró mejor movimiento por la IA, usando el primer movimiento legal como fallback.")
            start, end = legal_moves[0] # Toma el primer movimiento legal como fallback.
            return MoveClass(start, end, board, promotion_choice="q")
        return None # No hay movimientos legales en absoluto.

    # Asegurarse de que el movimiento final sea legal.
    # Esto es una doble verificación, ya que minimax solo debería devolver movimientos legales.
    final_legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
    if best_move_tuple not in final_legal_moves:
        print(f"⚠️ El movimiento {best_move_tuple} seleccionado por la IA es ilegal. Usando el primer movimiento legal como fallback.")
        if final_legal_moves:
            start, end = final_legal_moves[0]
            return MoveClass(start, end, board, promotion_choice="q")
        return None

    start, end = best_move_tuple # Desempaqueta el mejor movimiento.
    return MoveClass(start, end, board, promotion_choice="q") # Retorna el objeto Move.


