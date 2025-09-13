# IA/evaluation.py
piece_values = {"p":1,"n":3,"b":3,"r":5,"q":9,"k":0}

# Ejemplo simple de tabla de posición para peones
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

w_material = 1.0
w_position = 0.1
w_mobility = 0.05
w_king_safety = 0.2

def evaluate_board(board):
    score = 0
    from chessLogic.utils import get_all_moves

    for r in range(8):
        for c in range(8):
            piece = board.get_piece(r, c)
            if piece == "--": continue
            color = 1 if piece[0]=="w" else -1
            # Material
            score += color * piece_values[piece[1]] * w_material
            # Posición (ejemplo solo para peones)
            if piece[1]=="p":
                table_val = pawn_table[r][c] if piece[0]=="w" else pawn_table[7-r][c]
                score += color * w_position * table_val

    # Movilidad
    score += w_mobility * (len(get_all_moves(board,"w")) - len(get_all_moves(board,"b")))

    # Seguridad del rey
    if board.is_check("w"): score -= w_king_safety * 5
    if board.is_check("b"): score += w_king_safety * 5

    return score
