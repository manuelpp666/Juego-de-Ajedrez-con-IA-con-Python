# chessLogic/moves.py

def is_legal_move(chessboard, start_pos, end_pos, piece_type=None, pseudo_legal=False):
    from .rules import ChessRules

    board = chessboard.board
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    piece = board[start_row][start_col]
    target = board[end_row][end_col]

    if piece == "--":
        return False

    color = piece[0]
    p_type = piece[1] if piece_type is None else piece_type

    if target != "--" and target[0] == color:
        return False

    if p_type == "p":
        if _is_pawn_move(board, start_pos, end_pos, color):
            return True
        if ChessRules.en_passant(chessboard, start_pos, end_pos):
            return True
        return False
    elif p_type == "r":
        return _is_rook_move(board, start_pos, end_pos)
    elif p_type == "n":
        return _is_knight_move(start_pos, end_pos)
    elif p_type == "b":
        return _is_bishop_move(board, start_pos, end_pos)
    elif p_type == "q":
        return _is_queen_move(board, start_pos, end_pos)
    elif p_type == "k":
        if _is_king_move(start_pos, end_pos):
            return True
        # Solo chequear enroque si NO es pseudo-legal
        if not pseudo_legal:
            if (end_pos == (start_row, start_col + 2) and ChessRules.can_castle(chessboard, color, kingside=True)) or \
               (end_pos == (start_row, start_col - 2) and ChessRules.can_castle(chessboard, color, kingside=False)):
                return True
        return False

    return False

# ---------------------------
# Reglas geométricas
# ---------------------------

def _is_pawn_move(board, start, end, color):
    sr, sc = start
    er, ec = end
    direction = -1 if color == "w" else 1
    if sc == ec and board[er][ec] == "--":
        if er - sr == direction:
            return True
        if (sr == 6 and color == "w") or (sr == 1 and color == "b"):
            if er - sr == 2 * direction and board[sr + direction][sc] == "--":
                return True
    if abs(ec - sc) == 1 and er - sr == direction:
        if board[er][ec] != "--" and board[er][ec][0] != color:
            return True
    return False

def _is_rook_move(board, start, end):
    sr, sc = start
    er, ec = end
    if sr != er and sc != ec:
        return False
    step_r = 0 if sr == er else (1 if er > sr else -1)
    step_c = 0 if sc == ec else (1 if ec > sc else -1)
    r, c = sr + step_r, sc + step_c
    while (r, c) != (er, ec):
        if board[r][c] != "--":
            return False
        r += step_r
        c += step_c
    return True

def _is_knight_move(start, end):
    sr, sc = start
    er, ec = end
    return (abs(sr - er), abs(sc - ec)) in [(2, 1), (1, 2)]

def _is_bishop_move(board, start, end):
    sr, sc = start
    er, ec = end
    if abs(sr - er) != abs(sc - ec):
        return False
    step_r = 1 if er > sr else -1
    step_c = 1 if ec > sc else -1
    r, c = sr + step_r, sc + step_c
    while (r, c) != (er, ec):
        if board[r][c] != "--":
            return False
        r += step_r
        c += step_c
    return True

def _is_queen_move(board, start, end):
    return _is_rook_move(board, start, end) or _is_bishop_move(board, start, end)

def _is_king_move(start, end):
    sr, sc = start
    er, ec = end
    return abs(sr - er) <= 1 and abs(sc - ec) <= 1
