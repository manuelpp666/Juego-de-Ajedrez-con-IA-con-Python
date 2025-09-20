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

        # Capturas valiosas (MVV-LVA)
        if target != "--":
            score += 10 * piece_values.get(target[1], 0) - piece_values.get(piece[1], 0)

        # Promoción de peón
        if piece[1] == "p" and (end[0] == 0 or end[0] == 7):
            score += 50

        # Killer moves
        if depth in killer_moves and m in killer_moves[depth]:
            score += 75

        # History heuristic
        score += history_heuristic.get((piece, end), 0)

        return -score
    return sorted(moves, key=move_priority)

# --- Quiescence Search ---
def quiescence_search(board, alpha, beta, is_maximizing):
    stand_pat = evaluate_board(board)

    if is_maximizing:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    noisy_moves = []
    all_moves = MoveGenerator.generate_legal_moves(board, board.turn)
    for start, end in all_moves:
        piece = board.get_piece(*start)
        target = board.get_piece(*end)
        if target != "--" or (piece[1] == "p" and (end[0] in (0,7))):
            noisy_moves.append((start, end))

    noisy_moves = order_moves(board, noisy_moves, 0)

    for start, end in noisy_moves:
        m = MoveClass(start, end, board, promotion_choice="q")
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

# --- Minimax con poda, transposiciones, killer/history y LMR ---
def minimax(board, depth, alpha, beta, is_maximizing):
    board_hash = hash(str(board.board) + board.turn + str(board.en_passant_square) + str(board.castling_rights))

    if board_hash in transposition_table:
        entry = transposition_table[board_hash]
        if entry['depth'] >= depth:
            if entry['type'] == 'exact':
                return entry['score'], entry['best_move']
            if entry['type'] == 'lowerbound' and entry['score'] > alpha:
                alpha = entry['score']
            if entry['type'] == 'upperbound' and entry['score'] < beta:
                beta = entry['score']
            if alpha >= beta:
                return entry['score'], entry['best_move']

    if depth == 0:
        score = quiescence_search(board, alpha, beta, is_maximizing)
        transposition_table[board_hash] = {'score': score, 'depth': depth, 'type': 'exact', 'best_move': None}
        return score, None

    moves = MoveGenerator.generate_legal_moves(board, board.turn)
    if not moves:
        if ChessRules.is_in_check(board, board.turn):
            score = (-MATE_SCORE if board.turn == "w" else MATE_SCORE)
        else:
            score = STALEMATE_SCORE
        transposition_table[board_hash] = {'score': score, 'depth': depth, 'type': 'exact', 'best_move': None}
        return score, None

    moves = order_moves(board, moves, depth)
    best_move = None
    original_alpha = alpha
    entry_type = 'upperbound'

    if is_maximizing:
        max_eval = float('-inf')
        for i, (start, end) in enumerate(moves):
            m = MoveClass(start, end, board, promotion_choice="q")
            board.make_move(m)

            # Late Move Reductions (LMR)
            new_depth = depth - 1
            if depth > 2 and i > 3:
                target = board.get_piece(*end)
                if target == "--":  # no captura
                    new_depth -= 1

            eval_score, _ = minimax(board, new_depth, alpha, beta, False)
            board.undo_move()

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (start, end)

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                # Killer move
                if depth not in killer_moves:
                    killer_moves[depth] = []
                if (start, end) not in killer_moves[depth]:
                    killer_moves[depth].append((start, end))
                    if len(killer_moves[depth]) > 2:
                        killer_moves[depth].pop(0)
                # History heuristic
                piece = board.get_piece(*start)
                history_heuristic[(piece, end)] = history_heuristic.get((piece, end), 0) + depth * depth
                break

        if max_eval >= original_alpha:
            entry_type = 'lowerbound' if max_eval < beta else 'exact'
        transposition_table[board_hash] = {'score': max_eval, 'depth': depth, 'type': entry_type, 'best_move': best_move}
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for i, (start, end) in enumerate(moves):
            m = MoveClass(start, end, board, promotion_choice="q")
            board.make_move(m)

            # LMR
            new_depth = depth - 1
            if depth > 2 and i > 3:
                target = board.get_piece(*end)
                if target == "--":
                    new_depth -= 1

            eval_score, _ = minimax(board, new_depth, alpha, beta, True)
            board.undo_move()

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (start, end)

            beta = min(beta, eval_score)
            if beta <= alpha:
                # Killer move
                if depth not in killer_moves:
                    killer_moves[depth] = []
                if (start, end) not in killer_moves[depth]:
                    killer_moves[depth].append((start, end))
                    if len(killer_moves[depth]) > 2:
                        killer_moves[depth].pop(0)
                # History heuristic
                piece = board.get_piece(*start)
                history_heuristic[(piece, end)] = history_heuristic.get((piece, end), 0) + depth * depth
                break

        if min_eval <= original_alpha:
            entry_type = 'upperbound' if min_eval > alpha else 'exact'
        transposition_table[board_hash] = {'score': min_eval, 'depth': depth, 'type': entry_type, 'best_move': best_move}
        return min_eval, best_move

# --- Profundización iterativa ---
def get_best_move(board, max_depth=3, time_limit=10.0):
    start_time = time.time()
    best_move_tuple = None
    is_maximizing = (board.turn == "w")

    global transposition_table
    transposition_table = {}
    global killer_moves, history_heuristic
    killer_moves, history_heuristic = {}, {}

    prev_eval = 0
    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit:
            print(f"⏳ Tiempo límite alcanzado en profundidad {depth-1}.")
            break


        eval_score, move_tuple = minimax(board, depth, float('-inf'), float('inf'), is_maximizing)
        prev_eval = eval_score

        if move_tuple:
            best_move_tuple = move_tuple

    if not best_move_tuple:
        legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
        if legal_moves:
            print("⚠️ No se encontró mejor movimiento, usando fallback.")
            start, end = legal_moves[0]
            return MoveClass(start, end, board, promotion_choice="q")
        return None

    legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)
    if best_move_tuple not in legal_moves:
        print(f"⚠️ Movimiento ilegal detectado: {best_move_tuple}")
        if legal_moves:
            start, end = legal_moves[0]
            return MoveClass(start, end, board, promotion_choice="q")
        return None

    start, end = best_move_tuple
    return MoveClass(start, end, board, promotion_choice="q")
