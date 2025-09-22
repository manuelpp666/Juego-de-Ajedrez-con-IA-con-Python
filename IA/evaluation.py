# IA/evaluation.py
piece_values = {"p":100,"n":320,"b":330,"r":500,"q":900,"k":20000} # Valores ajustados

# --- Tablas de Posición (PSTs) ---
# Los valores se han escalado para ser más significativos y se han ajustado ligeramente
pawn_table = [
    [0,0,0,0,0,0,0,0],
    [50,50,50,50,50,50,50,50],
    [10,10,20,30,30,20,10,10],
    [5,5,10,25,25,10,5,5],
    [0,0,0,20,20,0,0,0],
    [5,-5,-10,0,0,-10,-5,5],
    [5,10,10,-20,-20,10,10,5],
    [0,0,0,0,0,0,0,0]
]

knight_table = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,0,0,0,0,-20,-40],
    [-30,0,10,15,15,10,0,-30],
    [-30,5,15,20,20,15,5,-30],
    [-30,0,15,20,20,15,0,-30],
    [-30,5,10,15,15,10,5,-30],
    [-40,-20,0,5,5,0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

bishop_table = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,0,0,0,0,0,0,-10],
    [-10,0,5,10,10,5,0,-10],
    [-10,5,5,10,10,5,5,-10],
    [-10,0,10,10,10,10,0,-10],
    [-10,10,10,10,10,10,10,-10],
    [-10,5,0,0,0,0,5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

rook_table = [
    [0,0,0,0,0,0,0,0],
    [5,10,10,10,10,10,10,5],
    [-5,0,0,0,0,0,0,-5],
    [-5,0,0,0,0,0,0,-5],
    [-5,0,0,0,0,0,0,-5],
    [-5,0,0,0,0,0,0,-5],
    [-5,0,0,0,0,0,0,-5],
    [0,0,0,5,5,0,0,0]
]

queen_table = [
    [-20,-10,-10,-5,-5,-10,-10,-20],
    [-10,0,0,0,0,0,0,-10],
    [-10,0,5,5,5,5,0,-10],
    [-5,0,5,5,5,5,0,-5],
    [0,0,5,5,5,5,0,0],
    [-10,5,5,5,5,5,0,-10],
    [-10,0,5,0,0,0,0,-10],
    [-20,-10,-10,-5,-5,-10,-10,-20]
]

king_table_mid = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20,20,0,0,0,0,20,20],
    [20,30,10,0,0,10,30,20]
]

king_table_end = [
    [-50,-40,-30,-20,-20,-30,-40,-50],
    [-30,-20,-10,0,0,-10,-20,-30],
    [-30,-10,20,30,30,20,-10,-30],
    [-30,-10,30,40,40,30,-10,-30],
    [-30,-10,30,40,40,30,-10,-30],
    [-30,-10,20,30,30,20,-10,-30],
    [-30,-30,0,0,0,0,-30,-30],
    [-50,-30,-30,-30,-30,-30,-30,-50]
]

# --- Pesos ajustados ---
w_material = 1.0
w_position = 0.15 # Mayor peso a la posición
w_mobility = 0.08 # Mayor peso a la movilidad
w_king_safety = 0.3 # Mayor peso a la seguridad del rey
w_pawn_structure = 0.05 # Nuevo peso para estructura de peones
w_other = 0.05

def evaluate_board(board):
    """
    Eval = w1*Material + w2*Posición + w3*Movilidad + w4*SeguridadRey + w5*EstructuraPeones + w6*OtrasHeurísticas
    """
    

    material_score = 0
    position_score = 0
    mobility_score = 0
    king_safety_score = 0
    pawn_structure_score = 0
    other_score = 0

    # --- Material + Posición ---
    for r in range(8):
        for c in range(8):
            piece = board.get_piece(r, c)
            if piece == "--":
                continue
            color_multiplier = 1 if piece[0] == "w" else -1
            p_type = piece[1]

            # Material
            material_score += color_multiplier * piece_values[p_type]

            # Posición con PST
            val = 0
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
                # Determinar si es endgame para usar la tabla de rey de endgame
                # Una heurística simple para endgame: si hay pocas piezas mayores
                num_major_pieces = 0
                for row_board in board.board:
                    for p in row_board:
                        if p != "--" and p[1] in ("q", "r"):
                            num_major_pieces += 1
                if num_major_pieces <= 4: # Arbitrario, se puede ajustar
                    val = king_table_end[r][c] if piece[0] == "w" else king_table_end[7-r][c]
                else:
                    val = king_table_mid[r][c] if piece[0] == "w" else king_table_mid[7-r][c]
            
            position_score += color_multiplier * val

    # --- Movilidad ---
    # Se usa MoveGenerator para obtener los movimientos pseudo-legales de forma más eficiente
    from IA.move_generator import MoveGenerator
    mobility_score = len(MoveGenerator.generate_pseudo_legal_moves(board, "w")) - \
                     len(MoveGenerator.generate_pseudo_legal_moves(board, "b"))

    # --- Seguridad del Rey ---
    # Penalización más fuerte por estar en jaque
    if board.is_check("w"):
        king_safety_score -= 100 # Penalización más alta
    if board.is_check("b"):
        king_safety_score += 100 # Penalización más alta

    # --- Estructura de Peones (Nueva heurística) ---
    # Peones doblados y aislados son malos
    for color in ["w", "b"]:
        pawn_count_by_col = [0] * 8
        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece == color + "p":
                    pawn_count_by_col[c] += 1
        
        for c in range(8):
            if pawn_count_by_col[c] > 1: # Peones doblados
                pawn_structure_score += (-20 if color == "w" else 20)
            
            # Peones aislados (sin peones amigos en columnas adyacentes)
            if pawn_count_by_col[c] > 0:
                is_isolated = True
                if c > 0 and pawn_count_by_col[c-1] > 0:
                    is_isolated = False
                if c < 7 and pawn_count_by_col[c+1] > 0:
                    is_isolated = False
                if is_isolated:
                    pawn_structure_score += (-15 if color == "w" else 15)

    # --- Otras heurísticas ---
    # Par de alfiles
    white_bishops = sum(1 for r in range(8) for c in range(8) if board.get_piece(r,c) == "wb")
    black_bishops = sum(1 for r in range(8) for c in range(8) if board.get_piece(r,c) == "bb")
    if white_bishops >= 2:
        other_score += 20 # Bonificación por par de alfiles
    if black_bishops >= 2:
        other_score -= 20

    # Control del centro (peones en d4, e4, d5, e5)
    center_squares = [(3,3), (3,4), (4,3), (4,4)]
    for r, c in center_squares:
        piece = board.get_piece(r, c)
        if piece == "wp":
            other_score += 10
        elif piece == "bp":
            other_score -= 10

    # --- Fórmula final ---
    score = (
        w_material * material_score +
        w_position * position_score +
        w_mobility * mobility_score +
        w_king_safety * king_safety_score +
        w_pawn_structure * pawn_structure_score +
        w_other * other_score
    )

    return score

