# IA/search.py
import time
from IA.evaluation import evaluate_board, piece_values
from IA.move_generator import MoveGenerator
from chessLogic.move import Move as MoveClass
from chessLogic.rules import ChessRules

MATE_SCORE = 1000000 # Aumentado para asegurar que el mate sea siempre la mejor opción
STALEMATE_SCORE = 0

# Tabla de transposiciones (simple diccionario)
transposition_table = {}

# Killer moves y history heuristic
killer_moves = {}       # killer_moves[depth] = [move1, move2]
history_heuristic = {}  # history_heuristic[(piece, end)] = score

# --- Move ordering mejorado ---
def order_moves(board, moves, depth):
    def move_priority(m):
        start, end = m
        piece = board.get_piece(*start)
        target = board.get_piece(*end)
        score = 0

        # Capturas valiosas (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
        if target != "--":
            # 10 * valor_pieza_capturada - valor_pieza_atacante
            score += 10 * piece_values.get(target[1], 0) - piece_values.get(piece[1], 0)

        # Promoción de peón
        if piece[1] == "p" and (end[0] == 0 or end[0] == 7):
            score += 900 # Valor de una reina

        # Killer moves (movimientos que causaron podas en otras ramas)
        if depth in killer_moves:
            for km in killer_moves[depth]:
                if m == km:
                    score += 800 # Alta prioridad para killer moves
                    break

        # History heuristic (movimientos que han sido buenos en el pasado)
        score += history_heuristic.get((piece, end), 0)

        return -score # Negativo para ordenar de mayor a menor prioridad

    return sorted(moves, key=move_priority)

# --- Quiescence Search ---
def quiescence_search(board, alpha, beta, is_maximizing):
    # Evaluar la posición actual (stand-pat)
    stand_pat = evaluate_board(board)

    if is_maximizing:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else: # is_minimizing
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    # Generar solo movimientos "ruidosos" (capturas y promociones)
    noisy_moves = []
    all_pseudo_moves = MoveGenerator.generate_pseudo_legal_moves(board, board.turn)
    for start, end in all_pseudo_moves:
        piece = board.get_piece(*start)
        target = board.get_piece(*end)
        # Es una captura o una promoción de peón
        if target != "--" or (piece[1] == "p" and (end[0] == 0 or end[0] == 7)):
            noisy_moves.append((start, end))

    # Ordenar movimientos ruidosos
    noisy_moves = order_moves(board, noisy_moves, 0) # depth 0 para quiescence

    for start, end in noisy_moves:
        # Crear un objeto Move para el movimiento actual
        m = MoveClass(start, end, board, promotion_choice="q") # Asumimos promoción a reina por defecto en búsqueda

        # Verificar si el movimiento es legal antes de hacerlo
        # Esto es crucial porque generate_pseudo_legal_moves no filtra jaques
        board.make_move(m)
        if ChessRules.is_in_check(board, board.turn == "w" and "b" or "w"): # Si el rey del jugador actual está en jaque después de mover
            board.undo_move()
            continue # Este movimiento es ilegal, saltar

        if is_maximizing:
            eval_score = quiescence_search(board, alpha, beta, False)
            board.undo_move()
            if eval_score >= beta:
                return beta
            alpha = max(alpha, eval_score)
        else: # is_minimizing
            eval_score = quiescence_search(board, alpha, beta, True)
            board.undo_move()
            if eval_score <= alpha:
                return alpha
            beta = min(beta, eval_score)

    return alpha if is_maximizing else beta

# --- Minimax con poda, transposiciones, killer/history y LMR ---
def minimax(board, depth, alpha, beta, is_maximizing):
    # Generar un hash único para la posición actual del tablero
    # Incluye el tablero, el turno, la casilla en passant y los derechos de enroque
    board_hash = hash(str(board.board) + board.turn + str(board.en_passant_square) + str(board.castling_rights))

    # Consultar la tabla de transposiciones
    if board_hash in transposition_table:
        entry = transposition_table[board_hash]
        if entry['depth'] >= depth: # Si la entrada es lo suficientemente profunda
            if entry['type'] == 'exact':
                return entry['score'], entry['best_move']
            if entry['type'] == 'lowerbound' and entry['score'] > alpha:
                alpha = entry['score']
            if entry['type'] == 'upperbound' and entry['score'] < beta:
                beta = entry['score']
            if alpha >= beta: # Poda por tabla de transposiciones
                return entry['score'], entry['best_move']

    # Caso base: profundidad 0, llamar a quiescence search
    if depth == 0:
        score = quiescence_search(board, alpha, beta, is_maximizing)
        # Guardar en la tabla de transposiciones
        transposition_table[board_hash] = {'score': score, 'depth': depth, 'type': 'exact', 'best_move': None}
        return score, None

    # Generar movimientos legales
    moves = MoveGenerator.generate_legal_moves(board, board.turn)
    
    # Si no hay movimientos legales (jaque mate o ahogado)
    if not moves:
        if ChessRules.is_in_check(board, board.turn):
            # Jaque mate: el jugador actual pierde
            score = (-MATE_SCORE if board.turn == "w" else MATE_SCORE)
        else:
            # Ahogado: empate
            score = STALEMATE_SCORE
        transposition_table[board_hash] = {'score': score, 'depth': depth, 'type': 'exact', 'best_move': None}
        return score, None

    # Ordenar movimientos para una poda alfa-beta más eficiente
    moves = order_moves(board, moves, depth)
    
    best_move = None
    original_alpha = alpha # Guardar alpha original para determinar el tipo de entrada en la TT
    entry_type = 'upperbound' # Por defecto, si no se poda, es un upperbound

    if is_maximizing:
        max_eval = float('-inf')
        for i, (start, end) in enumerate(moves):
            m = MoveClass(start, end, board, promotion_choice="q")
            board.make_move(m)

            # Late Move Reductions (LMR)
            # Reduce la profundidad de búsqueda para movimientos que no son capturas
            # y que se encuentran más tarde en la lista de movimientos ordenados.
            new_depth = depth - 1
            if depth >= 3 and i >= 4 and m.piece_captured == "--": # Ajustar umbrales
                new_depth -= 1 # Reducir la profundidad en 1
                if new_depth < 0: new_depth = 0 # Asegurar que no sea negativo

            eval_score, _ = minimax(board, new_depth, alpha, beta, False)
            board.undo_move()

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (start, end)

            alpha = max(alpha, eval_score)
            if beta <= alpha: # Poda beta
                # Actualizar Killer Moves
                if depth not in killer_moves:
                    killer_moves[depth] = []
                if (start, end) not in killer_moves[depth]:
                    killer_moves[depth].append((start, end))
                    if len(killer_moves[depth]) > 2: # Mantener solo los 2 mejores killer moves
                        killer_moves[depth].pop(0)
                # Actualizar History Heuristic
                piece = board.get_piece(*start)
                history_heuristic[(piece, end)] = history_heuristic.get((piece, end), 0) + depth * depth
                entry_type = 'lowerbound' # Se encontró un límite inferior
                break # Poda

        # Guardar en la tabla de transposiciones
        if max_eval >= original_alpha:
            entry_type = 'exact' if max_eval < beta else 'lowerbound'
        transposition_table[board_hash] = {'score': max_eval, 'depth': depth, 'type': entry_type, 'best_move': best_move}
        return max_eval, best_move
    else: # is_minimizing
        min_eval = float('inf')
        for i, (start, end) in enumerate(moves):
            m = MoveClass(start, end, board, promotion_choice="q")
            board.make_move(m)

            # Late Move Reductions (LMR)
            new_depth = depth - 1
            if depth >= 3 and i >= 4 and m.piece_captured == "--": # Ajustar umbrales
                new_depth -= 1
                if new_depth < 0: new_depth = 0

            eval_score, _ = minimax(board, new_depth, alpha, beta, True)
            board.undo_move()

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (start, end)

            beta = min(beta, eval_score)
            if beta <= alpha: # Poda alfa
                # Actualizar Killer Moves
                if depth not in killer_moves:
                    killer_moves[depth] = []
                if (start, end) not in killer_moves[depth]:
                    killer_moves[depth].append((start, end))
                    if len(killer_moves[depth]) > 2:
                        killer_moves[depth].pop(0)
                # Actualizar History Heuristic
                piece = board.get_piece(*start)
                history_heuristic[(piece, end)] = history_heuristic.get((piece, end), 0) + depth * depth
                entry_type = 'upperbound' # Se encontró un límite superior
                break # Poda

        # Guardar en la tabla de transposiciones
        if min_eval <= original_alpha:
            entry_type = 'exact' if min_eval > alpha else 'upperbound'
        transposition_table[board_hash] = {'score': min_eval, 'depth': depth, 'type': entry_type, 'best_move': best_move}
        return min_eval, best_move

# --- Profundización iterativa ---
def get_best_move(board, max_depth=3, time_limit=10.0):
    start_time = time.time()
    best_move_tuple = None
    is_maximizing = (board.turn == "w")

    # Reiniciar tablas para cada nueva búsqueda
    global transposition_table, killer_moves, history_heuristic
    transposition_table = {}
    killer_moves = {d: [] for d in range(max_depth + 1)} # Inicializar killer moves para cada profundidad
    history_heuristic = {}

    # Iterative Deepening
    for depth in range(1, max_depth + 1):
        # Verificar límite de tiempo
        if time.time() - start_time > time_limit:
            print(f"⏳ Tiempo límite alcanzado en profundidad {depth-1}. Usando el mejor movimiento encontrado hasta ahora.")
            break

        # Llamar a minimax para la profundidad actual
        eval_score, move_tuple = minimax(board, depth, float('-inf'), float('inf'), is_maximizing)
        
        # Si se encontró un movimiento válido, actualizar el mejor movimiento global
        if move_tuple:
            best_move_tuple = move_tuple
            # print(f"Profundidad {depth}: Mejor movimiento {move_tuple}, Evaluación: {eval_score}")
        else:
            # Si no se encontró un movimiento en esta profundidad, y no hay un best_move_tuple previo,
            # significa que no hay movimientos legales o algo salió mal.
            # Esto debería ser manejado por la lógica de jaque mate/ahogado en minimax.
            pass

    # Fallback si no se encontró ningún movimiento (ej. al inicio del juego o si el tiempo se agota muy rápido)
    if not best_move_tuple:
        legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
        if legal_moves:
            print("⚠️ No se encontró mejor movimiento por la IA, usando el primer movimiento legal como fallback.")
            start, end = legal_moves[0]
            return MoveClass(start, end, board, promotion_choice="q")
        return None # No hay movimientos legales en absoluto

    # Asegurarse de que el movimiento final sea legal
    # Esto es una doble verificación, ya que minimax solo debería devolver movimientos legales
    final_legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
    if best_move_tuple not in final_legal_moves:
        print(f"⚠️ El movimiento {best_move_tuple} seleccionado por la IA es ilegal. Usando el primer movimiento legal como fallback.")
        if final_legal_moves:
            start, end = final_legal_moves[0]
            return MoveClass(start, end, board, promotion_choice="q")
        return None

    start, end = best_move_tuple
    return MoveClass(start, end, board, promotion_choice="q")
