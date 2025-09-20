# IA/evaluation.py
piece_values = {"p":1,"n":3,"b":3,"r":5,"q":9,"k":0}

# --- Tablas de Posición (PSTs) ---
pawn_table = [
    [0,0,0,0,0,0,0,0],
    [5,5,5,5,5,5,5,5],
    [1,1,2,3,3,2,1,1],
    [0.5,0.5,1,2,2,1,0.5,0.5],
    [0,0,0,2,2,0,0,0],
    [0.5,-0.5,-1,0,0,-1,-0.5,0.5],
    [0.5,1,1,-2,-2,1,1,0.5],
    [0,0,0,0,0,0,0,0]
]

knight_table = [
    [-5,-4,-3,-3,-3,-3,-4,-5],
    [-4,-2,0,0,0,0,-2,-4],
    [-3,0,1,1.5,1.5,1,0,-3],
    [-3,0.5,1.5,2,2,1.5,0.5,-3],
    [-3,0,1.5,2,2,1.5,0,-3],
    [-3,0.5,1,1.5,1.5,1,0.5,-3],
    [-4,-2,0,0.5,0.5,0,-2,-4],
    [-5,-4,-3,-3,-3,-3,-4,-5]
]

bishop_table = [
    [-2,-1,-1,-1,-1,-1,-1,-2],
    [-1,0,0,0,0,0,0,-1],
    [-1,0,0.5,1,1,0.5,0,-1],
    [-1,0.5,0.5,1,1,0.5,0.5,-1],
    [-1,0,1,1,1,1,0,-1],
    [-1,1,1,1,1,1,1,-1],
    [-1,0.5,0,0,0,0,0.5,-1],
    [-2,-1,-1,-1,-1,-1,-1,-2]
]

rook_table = [
    [0,0,0,0,0,0,0,0],
    [0.5,1,1,1,1,1,1,0.5],
    [-0.5,0,0,0,0,0,0,-0.5],
    [-0.5,0,0,0,0,0,0,-0.5],
    [-0.5,0,0,0,0,0,0,-0.5],
    [-0.5,0,0,0,0,0,0,-0.5],
    [-0.5,0,0,0,0,0,0,-0.5],
    [0,0,0,0.5,0.5,0,0,0]
]

queen_table = [
    [-2,-1,-1,-0.5,-0.5,-1,-1,-2],
    [-1,0,0,0,0,0,0,-1],
    [-1,0,0.5,0.5,0.5,0.5,0,-1],
    [-0.5,0,0.5,0.5,0.5,0.5,0,-0.5],
    [0,0,0.5,0.5,0.5,0.5,0,0],
    [-1,0.5,0.5,0.5,0.5,0.5,0,-1],
    [-1,0,0.5,0,0,0,0,-1],
    [-2,-1,-1,-0.5,-0.5,-1,-1,-2]
]

king_table_mid = [
    [-3,-4,-4,-5,-5,-4,-4,-3],
    [-3,-4,-4,-5,-5,-4,-4,-3],
    [-3,-4,-4,-5,-5,-4,-4,-3],
    [-3,-4,-4,-5,-5,-4,-4,-3],
    [-2,-3,-3,-4,-4,-3,-3,-2],
    [-1,-2,-2,-2,-2,-2,-2,-1],
    [2,2,0,0,0,0,2,2],
    [2,3,1,0,0,1,3,2]
]

king_table_end = [
    [-5,-4,-3,-2,-2,-3,-4,-5],
    [-3,-2,-1,0,0,-1,-2,-3],
    [-3,-1,2,3,3,2,-1,-3],
    [-3,-1,3,4,4,3,-1,-3],
    [-3,-1,3,4,4,3,-1,-3],
    [-3,-1,2,3,3,2,-1,-3],
    [-3,-3,0,0,0,0,-3,-3],
    [-5,-3,-3,-3,-3,-3,-3,-5]
]

# --- Pesos ---
w_material = 1.0
w_position = 0.1
w_mobility = 0.05
w_king_safety = 0.2
w_other = 0.1

def evaluate_board(board):
    """
    Eval = w1*Material + w2*Posición + w3*Movilidad + w4*SeguridadRey + w5*OtrasHeurísticas
    """
    from chessLogic.utils import get_all_moves

    material_score = 0
    position_score = 0
    mobility_score = 0
    king_safety_score = 0
    other_score = 0

    # --- Material + Posición ---
    for r in range(8):
        for c in range(8):
            piece = board.get_piece(r, c)
            if piece == "--":
                continue
            color = 1 if piece[0] == "w" else -1
            p_type = piece[1]

            # Material
            material_score += color * piece_values[p_type]

            # Posición con PST
            if p_type == "p":
                val = pawn_table[r][c] if piece[0] == "w" else pawn_table[7-r][c]
            elif p_type == "n":
                val = knight_table[r][c] if piece[0] == "w" else knight_table[7-r][c]
            elif p_type == "b":
                val = bishop_table[r][c] if piece[0] == "w" else bishop_table[7-r][c]
            elif p_type == "r":
                val = rook_table[r][c] if piece[0] == "w" else rook_table[7-r][c]
            elif p_type == "q":
                val = queen_table[r][c] if piece[0] == "w" else queen_table[7-r][c]
            elif p_type == "k":
                # Solo midgame de momento, podrías interpolar con endgame
                val = king_table_mid[r][c] if piece[0] == "w" else king_table_mid[7-r][c]
            else:
                val = 0

            position_score += color * val

    # --- Movilidad ---
    mobility_score = len(get_all_moves(board, "w")) - len(get_all_moves(board, "b"))

    # --- Seguridad del Rey ---
    if board.is_check("w"):
        king_safety_score -= 5
    if board.is_check("b"):
        king_safety_score += 5

    # --- Otras heurísticas ---
    # Ejemplo: par de alfiles
    white_bishops = sum(1 for r in range(8) for c in range(8) if board.get_piece(r,c) == "wb")
    black_bishops = sum(1 for r in range(8) for c in range(8) if board.get_piece(r,c) == "bb")
    if white_bishops >= 2:
        other_score += 0.5
    if black_bishops >= 2:
        other_score -= 0.5

    # --- Fórmula final ---
    score = (
        w_material * material_score +
        w_position * position_score +
        w_mobility * mobility_score +
        w_king_safety * king_safety_score +
        w_other * other_score
    )

    return score
