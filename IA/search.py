# IA/search.py
import time
from IA.evaluation import evaluate_board, piece_values
from IA.move_generator import MoveGenerator
from chessLogic.move import Move as MoveClass
from chessLogic.rules import ChessRules

MATE_SCORE = 100000
STALEMATE_SCORE = 0

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
                score += 10 * abs(piece_values[target[1]]) - piece_values[piece[1]]
            except KeyError:
                pass

        # Promoción de peón
        if piece[1] == "p" and (end[0] == 0 or end[0] == 7):
            score += 50

        # Jaque → verificar con el oponente correcto
        opponent = "b" if board.turn == "w" else "w"
        temp_move = MoveClass(start, end, board, promotion_choice="q")
        board.make_move(temp_move)
        if ChessRules.is_in_check(board, opponent):
            score += 20
        board.undo_move()

        return -score

    return sorted(moves, key=move_priority)

# --- Minimax con poda ---
def minimax(board, depth, alpha, beta, is_maximizing):
    if depth == 0:
        return evaluate_board(board), None

    moves = MoveGenerator.generate_legal_moves(board, board.turn)
    if not moves:
        if ChessRules.is_in_check(board, board.turn):
            return (-MATE_SCORE if board.turn == "w" else MATE_SCORE), None
        else:
            return STALEMATE_SCORE, None

    moves = order_moves(board, moves)
    best_move = None

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
                break
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
                break
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

    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit:
            break
        eval_score, move_tuple = minimax(board, depth, float('-inf'), float('inf'), is_maximizing)
        if move_tuple:
            best_move_tuple = move_tuple

    if not best_move_tuple:
        return None

    # ✅ Filtrar: asegurarnos de que el movimiento devuelto esté en los legales
    legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
    if best_move_tuple not in legal_moves:
        print(f"⚠️ Movimiento ilegal detectado y descartado: {best_move_tuple}")
        return None

    start, end = best_move_tuple
    return MoveClass(start, end, board, promotion_choice="q")
