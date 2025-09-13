# IA/search.py
"""
Minimax con poda Alfa-Beta usando MoveGenerator.generate_legal_moves.
Retorna la mejor jugada como TUPLA (start, end) desde la búsqueda; la
conversión a Move se hace sólo cuando se va a aplicar en el tablero real.
Esto evita que objetos Move (con referencias al tablero) viajen por la recursión.
"""

from IA.evaluation import evaluate_board
from IA.move_generator import MoveGenerator

# Puntajes extremos para mate/ahogado
MATE_SCORE = 100000
STALEMATE_SCORE = 0

def minimax(board, depth, alpha, beta, is_maximizing):
    """
    Minimax con poda Alfa-Beta.
    Devuelve: (best_score, best_move_tuple) donde best_move_tuple es (start, end) o None.
    """

    # 1) Caso base: profundidad 0 -> evaluación estática
    if depth == 0:
        return evaluate_board(board), None

    # 2) Generar movimientos legales del jugador que está a mover (board.turn)
    moves = MoveGenerator.generate_legal_moves(board, board.turn)

    # 2a) Si no hay movimientos: mate o tablas
    if not moves:
        if board.is_check(board.turn):
            # El que está por mover está en mate: perderá
            # Si quien está en mate es el blanco -> resultado muy negativo para blancas (score bajo)
            return (-MATE_SCORE if board.turn == "w" else MATE_SCORE), None
        else:
            # Ahogado (tablas)
            return STALEMATE_SCORE, None

    # 3) Orden simple: capturas primero (mejora poda)
    moves.sort(key=lambda m: 0 if board.get_piece(*m[1]) != "--" else 1)

    best_move = None

    # 4) Minimax con alfa-beta (las llamadas intercambian is_maximizing True/False)
    if is_maximizing:
        max_eval = float('-inf')
        for start, end in moves:
            # Aplicar movimiento (crear Move CON EL TABLERO actual y aplicar)
            from chessLogic.move import Move as MoveClass
            m = MoveClass(start, end, board, promotion_choice="q")
            board.make_move(m)

            eval_score, _ = minimax(board, depth - 1, alpha, beta, False)

            board.undo_move()

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (start, end)

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # poda

        return max_eval, best_move

    else:
        min_eval = float('inf')
        for start, end in moves:
            from chessLogic.move import Move as MoveClass
            m = MoveClass(start, end, board, promotion_choice="q")
            board.make_move(m)

            eval_score, _ = minimax(board, depth - 1, alpha, beta, True)

            board.undo_move()

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (start, end)

            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # poda

        return min_eval, best_move


def get_best_move(board, depth):
    """
    Función auxiliar para llamar desde gui.py.
    Devuelve un objeto Move listo para aplicar (o None).
    """
    # Si la partida ya terminó, no buscar
    if board.is_checkmate("w") or board.is_checkmate("b"):
        return None
    # Buscar la mejor jugada con minimax alfa-beta
    is_maximizing = (board.turn == "w")
    _, best_move_tuple = minimax(board, depth, float('-inf'), float('inf'), is_maximizing)
    if not best_move_tuple:
        return None

    # Crear Move con el tablero actual antes de devolverlo (asi contiene la info correcta)
    from chessLogic.move import Move as MoveClass
    start, end = best_move_tuple
    return MoveClass(start, end, board, promotion_choice="q")
