# IA/a_star.py
import heapq
import itertools
from IA.evaluation import evaluate_board
from IA.move_generator import MoveGenerator
from chessLogic.move import Move


def get_best_move_astar(board, depth_limit=2, beam_width=5):
    """
    Algoritmo A* adaptado para ajedrez (modo fácil).
    Usa evaluación estática como heurística, con límite de profundidad y beam search.
    Se apoya en make_move / undo_move en vez de copiar tableros completos.
    """

    counter = itertools.count()  # contador único para cada entrada

    # Nodo en la cola: (f, g, h, depth, move_sequence)
    start_eval = evaluate_board(board)
    start_node = (start_eval, 0, start_eval, 0, [])

    # heapq = [ (prioridad, id_unico, nodo) ]
    frontier = [(-start_node[0], next(counter), start_node)]
    best_move = None

    while frontier:
        _, _, (f, g, h, depth, move_seq) = heapq.heappop(frontier)

        # Si alcanzamos la profundidad límite, devolvemos el primer movimiento
        if depth >= depth_limit:
            if move_seq:
                return move_seq[0]
            continue

        # Generar movimientos legales desde el tablero actual
        legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)

        # Asegurar que todos sean instancias de Move
        fixed_moves = []
        for m in legal_moves:
            if isinstance(m, Move):
                fixed_moves.append(m)
            else:
                try:
                    start_sq, end_sq = m
                    fixed_moves.append(Move(start_sq, end_sq, board))
                except Exception:
                    continue

        scored_moves = []
        for move in fixed_moves:
            board.make_move(move)
            eval_score = evaluate_board(board)
            board.undo_move()

            if board.turn == "b":
                h_new = -eval_score
            else:
                h_new = eval_score

            g_new = g + 1
            f_new = g_new + h_new
            scored_moves.append((f_new, g_new, h_new, move))

        # Beam search
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        scored_moves = scored_moves[:beam_width]

        for f_new, g_new, h_new, move in scored_moves:
            board.make_move(move)
            heapq.heappush(
                frontier,
                (-f_new, next(counter), (f_new, g_new, h_new, depth + 1, move_seq + [move]))
            )
            board.undo_move()

    return best_move
