# IA/search.py
from IA.evaluation import evaluate_board
from chessLogic.move import Move

def minimax(board, depth, is_maximizing):
    """
    Algoritmo minimax básico.
    board: instancia de ChessBoard
    depth: nivel de profundidad
    is_maximizing: True si es turno de las blancas (max), False si es de las negras (min)
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None
    
    best_move = None

    if is_maximizing:
        max_eval = float('-inf')
        for move in board.get_legal_moves():
            board.make_move(move)
            eval_score, _ = minimax(board, depth - 1, False)
            board.undo_move()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in board.get_legal_moves():
            board.make_move(move)
            eval_score, _ = minimax(board, depth - 1, True)
            board.undo_move()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
        return min_eval, best_move
