piece_values = {
    "p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 0,
}

def evaluate_board(board):
    """
    Retorna un score positivo si blancas tienen ventaja,
    negativo si negras tienen ventaja.
    """
    score = 0
    for row in board.board:
        for piece in row:
            if piece == "--":
                continue
            color = 1 if piece[0] == "w" else -1
            value = piece_values[piece[1]]
            score += color * value
    return score
