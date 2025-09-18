# IA/search.py
import time
from IA.evaluation import evaluate_board, piece_values
from IA.move_generator import MoveGenerator
from chessLogic.move import Move as MoveClass
from chessLogic.rules import ChessRules

MATE_SCORE = 100000
STALEMATE_SCORE = 0

# Tabla de transposiciones (simple diccionario)
transposition_table = {}

# --- Move ordering ---
def order_moves(board, moves):
    """
    Ordena jugadas para mejorar la poda:
    1. Capturas (más valiosas primero).
    2. Jaques.
    3. Promociones.
    4. Otras.
    """
    def move_priority(m):
        start, end = m
        piece = board.get_piece(*start)
        target = board.get_piece(*end)

        score = 0
        # Capturas valiosas primero (MVV-LVA)
        if target != "--":
            try:
                # 10 * valor_pieza_capturada - valor_pieza_atacante
                score += 10 * piece_values.get(target[1], 0) - piece_values.get(piece[1], 0)
            except KeyError:
                pass

        # Promoción de peón
        if piece[1] == "p" and (end[0] == 0 or end[0] == 7):
            score += 50

        # Jaque → verificar con el oponente correcto
        # Solo si el movimiento es legal, ya que generate_legal_moves ya filtra
        # No es necesario simular aquí si ya se hizo en generate_legal_moves
        # Pero para el ordenamiento, podemos hacer una simulación ligera
        temp_move = MoveClass(start, end, board, promotion_choice="q")
        board.make_move(temp_move)
        opponent = "b" if board.turn == "w" else "w"
        if ChessRules.is_in_check(board, opponent):
            score += 20
        board.undo_move()

        return -score # Negativo para ordenar de mayor a menor prioridad

    return sorted(moves, key=move_priority)

# --- Quiescence Search ---
def quiescence_search(board, alpha, beta, is_maximizing):
    """
    Extiende la búsqueda en posiciones "ruidosas" (capturas, promociones)
    para evitar el efecto horizonte.
    """
    stand_pat = evaluate_board(board)

    if is_maximizing:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    # Solo considera movimientos "ruidosos" (capturas y promociones)
    noisy_moves = []
    all_moves = MoveGenerator.generate_legal_moves(board, board.turn)
    for start, end in all_moves:
        piece = board.get_piece(*start)
        target = board.get_piece(*end)
        if target != "--" or (piece[1] == "p" and (end[0] == 0 or end[0] == 7)): # Es captura o promoción
            noisy_moves.append((start, end))
    
    noisy_moves = order_moves(board, noisy_moves) # Ordenar también los movimientos ruidosos

    for start, end in noisy_moves:
        m = MoveClass(start, end, board, promotion_choice="q") # Asumir promoción a reina por simplicidad en quiescence
        board.make_move(m)

        if is_maximizing:
            eval_score = quiescence_search(board, alpha, beta, False)
            board.undo_move()
            if eval_score >= beta:
                return beta
            alpha = max(alpha, eval_score)
        else:
            eval_score = quiescence_search(board, alpha, beta, True)
            board.undo_move()
            if eval_score <= alpha:
                return alpha
            beta = min(beta, eval_score)
    return alpha if is_maximizing else beta


# --- Minimax con poda y tabla de transposiciones ---
def minimax(board, depth, alpha, beta, is_maximizing):
    # Generar una clave única para el estado del tablero
    board_hash = hash(str(board.board) + board.turn + str(board.en_passant_square) + str(board.castling_rights))

    # Consultar la tabla de transposiciones
    if board_hash in transposition_table:
        entry = transposition_table[board_hash]
        if entry['depth'] >= depth:
            # Si la entrada es lo suficientemente profunda, podemos usarla
            # Aquí se necesitaría un manejo más sofisticado de alpha/beta bounds
            # Por simplicidad, si es un valor exacto, lo usamos.
            # Para un nivel intermedio, esto es suficiente.
            if entry['type'] == 'exact':
                return entry['score'], entry['best_move']
            # Si es un lowerbound y es mejor que alpha, actualizamos alpha
            if entry['type'] == 'lowerbound' and entry['score'] > alpha:
                alpha = entry['score']
            # Si es un upperbound y es peor que beta, actualizamos beta
            if entry['type'] == 'upperbound' and entry['score'] < beta:
                beta = entry['score']
            if alpha >= beta: # Si la ventana se ha cerrado, podemos usar el resultado
                return entry['score'], entry['best_move']


    if depth == 0:
        # En lugar de solo evaluar, llamamos a la búsqueda de quiescencia
        score = quiescence_search(board, alpha, beta, is_maximizing)
        # Almacenar en la tabla de transposiciones
        transposition_table[board_hash] = {'score': score, 'depth': depth, 'type': 'exact', 'best_move': None}
        return score, None

    moves = MoveGenerator.generate_legal_moves(board, board.turn)
    if not moves:
        if ChessRules.is_in_check(board, board.turn):
            score = (-MATE_SCORE if board.turn == "w" else MATE_SCORE)
        else:
            score = STALEMATE_SCORE
        # Almacenar en la tabla de transposiciones
        transposition_table[board_hash] = {'score': score, 'depth': depth, 'type': 'exact', 'best_move': None}
        return score, None

    moves = order_moves(board, moves)
    best_move = None
    original_alpha = alpha # Guardar alpha original para la tabla de transposiciones
    entry_type = 'upperbound' # Por defecto, si no encontramos un movimiento mejor, es un upperbound

    if is_maximizing:
        max_eval = float('-inf')
        for start, end in moves:
            m = MoveClass(start, end, board, promotion_choice="q")
            board.make_move(m)

            eval_score, _ = minimax(board, depth - 1, alpha, beta, False)
            board.undo_move()

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (start, end)

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break # Poda Beta
        
        # Almacenar en la tabla de transposiciones
        if max_eval >= original_alpha: # Si el valor es mayor o igual al alpha original, es un lowerbound o exacto
            entry_type = 'lowerbound' if max_eval < beta else 'exact'
        transposition_table[board_hash] = {'score': max_eval, 'depth': depth, 'type': entry_type, 'best_move': best_move}
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for start, end in moves:
            m = MoveClass(start, end, board, promotion_choice="q")
            board.make_move(m)

            eval_score, _ = minimax(board, depth - 1, alpha, beta, True)
            board.undo_move()

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (start, end)

            beta = min(beta, eval_score)
            if beta <= alpha:
                break # Poda Alpha
        
        # Almacenar en la tabla de transposiciones
        if min_eval <= original_alpha: # Si el valor es menor o igual al alpha original, es un upperbound o exacto
            entry_type = 'upperbound' if min_eval > alpha else 'exact'
        transposition_table[board_hash] = {'score': min_eval, 'depth': depth, 'type': entry_type, 'best_move': best_move}
        return min_eval, best_move

# --- Profundización iterativa ---
def get_best_move(board, max_depth=3, time_limit=10.0):
    """
    Busca el mejor movimiento con profundización iterativa.
    max_depth: profundidad máxima.
    time_limit: límite de tiempo en segundos.
    """
    start_time = time.time()
    best_move_tuple = None
    is_maximizing = (board.turn == "w")

    # Limpiar la tabla de transposiciones al inicio de cada búsqueda principal
    global transposition_table
    transposition_table = {}

    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit:
            print(f"Tiempo límite alcanzado en profundidad {depth-1}. Usando el mejor movimiento encontrado hasta ahora.")
            break
        
        # Asegurarse de que la llamada a minimax use la profundidad correcta
        eval_score, move_tuple = minimax(board, depth, float('-inf'), float('inf'), is_maximizing)
        
        if move_tuple:
            best_move_tuple = move_tuple
        else:
            # Si no se encontró un movimiento en esta profundidad, y no hay un best_move_tuple previo,
            # podría significar que no hay movimientos legales o que la profundidad es muy baja.
            # En un juego real, esto no debería pasar si hay movimientos legales.
            # Para evitar retornar None si hay movimientos, podemos intentar con la profundidad anterior.
            if not best_move_tuple and depth > 1:
                print(f"No se encontró un movimiento en profundidad {depth}, intentando con la anterior.")
                # Esto es un parche; lo ideal es que minimax siempre devuelva un movimiento si hay.
                # Podríamos re-ejecutar minimax con depth-1 o confiar en el best_move_tuple de la iteración anterior.
                pass 

    if not best_move_tuple:
        # Si después de todas las profundidades no hay un best_move_tuple,
        # significa que no hay movimientos legales o algo salió mal.
        # En este caso, intentamos generar un movimiento legal simple como fallback.
        legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
        if legal_moves:
            print("⚠️ No se encontró el mejor movimiento con IA, seleccionando el primer movimiento legal.")
            start, end = legal_moves[0]
            return MoveClass(start, end, board, promotion_choice="q")
        else:
            return None # No hay movimientos legales

    # ✅ Filtrar: asegurarnos de que el movimiento devuelto esté en los legales
    # Esta comprobación es redundante si minimax solo genera movimientos legales,
    # pero es una buena salvaguarda.
    legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
    if best_move_tuple not in legal_moves:
        print(f"⚠️ Movimiento ilegal detectado y descartado: {best_move_tuple}")
        # Si el mejor movimiento de la IA es ilegal, buscamos otro.
        # Esto puede ocurrir si la tabla de transposiciones o la lógica de poda
        # no manejan correctamente los movimientos que dejan al rey en jaque.
        # Como fallback, podemos intentar el primer movimiento legal.
        if legal_moves:
            start, end = legal_moves[0]
            return MoveClass(start, end, board, promotion_choice="q")
        return None

    start, end = best_move_tuple
    return MoveClass(start, end, board, promotion_choice="q")
