# IA/evaluation.py
# Valores de las piezas en puntos. Ajustados para dar más peso a las piezas mayores.
piece_values = {"p":100,"n":320,"b":330,"r":500,"q":900,"k":20000} 

# --- Tablas de Posición (PSTs - Piece-Square Tables) ---
# Estas tablas asignan un valor a cada casilla del tablero para cada tipo de pieza,
# reflejando la deseabilidad de que una pieza ocupe esa casilla.
# Los valores se han escalado para ser más significativos y se han ajustado ligeramente.

# Tabla para peones: favorece el avance y el control central.
pawn_table = [
    [0,0,0,0,0,0,0,0],
    [50,50,50,50,50,50,50,50], # Peones avanzados valen más.
    [10,10,20,30,30,20,10,10],
    [5,5,10,25,25,10,5,5],
    [0,0,0,20,20,0,0,0],
    [5,-5,-10,0,0,-10,-5,5],
    [5,10,10,-20,-20,10,10,5], # Peones en la fila inicial valen menos.
    [0,0,0,0,0,0,0,0]
]

# Tabla para caballos: favorece el centro y penaliza las esquinas.
knight_table = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,0,0,0,0,-20,-40],
    [-30,0,10,15,15,10,0,-30],
    [-30,5,15,20,20,15,5,-30], # Caballos en el centro valen más.
    [-30,0,15,20,20,15,0,-30],
    [-30,5,10,15,15,10,5,-30],
    [-40,-20,0,5,5,0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

# Tabla para alfiles: favorece las diagonales abiertas y el centro.
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

# Tabla para torres: favorece las columnas abiertas y la séptima fila.
rook_table = [
    [0,0,0,0,0,0,0,0],
    [5,10,10,10,10,10,10,5], # Torres en la segunda fila (para blancas) valen más.
    [-5,0,0,0,0,0,0,-5],
    [-5,0,0,0,0,0,0,-5],
    [-5,0,0,0,0,0,0,-5],
    [-5,0,0,0,0,0,0,-5],
    [-5,0,0,0,0,0,0,-5],
    [0,0,0,5,5,0,0,0]
]

# Tabla para reinas: similar a alfiles y torres, favorece el centro.
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

# Tabla para reyes en el medio juego: penaliza el centro, favorece la seguridad detrás de peones.
king_table_mid = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20,20,0,0,0,0,20,20], # Favorece la seguridad del rey detrás de peones.
    [20,30,10,0,0,10,30,20]
]

# Tabla para reyes en el final del juego: favorece el centro para participar en el ataque.
king_table_end = [
    [-50,-40,-30,-20,-20,-30,-40,-50],
    [-30,-20,-10,0,0,-10,-20,-30],
    [-30,-10,20,30,30,20,-10,-30],
    [-30,-10,30,40,40,30,-10,-30], # Favorece el rey en el centro.
    [-30,-10,30,40,40,30,-10,-30],
    [-30,-10,20,30,30,20,-10,-30],
    [-30,-30,0,0,0,0,-30,-30],
    [-50,-30,-30,-30,-30,-30,-30,-50]
]

# --- Pesos ajustados para cada componente de la función de evaluación ---
# Estos pesos determinan la importancia relativa de cada heurística.
w_material = 1.0 # Peso del material (valor de las piezas).
w_position = 0.15 # Mayor peso a la posición (PSTs).
w_mobility = 0.08 # Mayor peso a la movilidad (número de movimientos posibles).
w_king_safety = 0.3 # Mayor peso a la seguridad del rey.
w_pawn_structure = 0.05 # Nuevo peso para la estructura de peones (peones doblados, aislados).
w_other = 0.05 # Peso para otras heurísticas menores.

def evaluate_board(board):
    """
    Función de evaluación estática del tablero de ajedrez.
    Calcula una puntuación numérica que representa la ventaja de las blancas sobre las negras.
    Una puntuación positiva indica ventaja para las blancas, negativa para las negras.
    
    La evaluación se basa en una combinación ponderada de varias heurísticas:
    Eval = w1*Material + w2*Posición + w3*Movilidad + w4*SeguridadRey + w5*EstructuraPeones + w6*OtrasHeurísticas
    
    Args:
        board (ChessBoard): La instancia actual del tablero de ajedrez.
        
    Returns:
        float: La puntuación de evaluación del tablero.
    """
    

    material_score = 0 # Puntuación por el valor de las piezas.
    position_score = 0 # Puntuación por la posición de las piezas (PSTs).
    mobility_score = 0 # Puntuación por la movilidad de las piezas.
    king_safety_score = 0 # Puntuación por la seguridad del rey.
    pawn_structure_score = 0 # Puntuación por la estructura de peones.
    other_score = 0 # Puntuación por otras heurísticas.

    # --- Material + Posición ---
    # Itera sobre cada casilla del tablero para evaluar material y posición.
    for r in range(8):
        for c in range(8):
            piece = board.get_piece(r, c) # Obtiene la pieza en la casilla (r, c).
            if piece == "--": # Si la casilla está vacía, continúa.
                continue
            
            # Multiplicador para el color: +1 para blancas, -1 para negras.
            color_multiplier = 1 if piece[0] == "w" else -1
            p_type = piece[1] # Tipo de la pieza (p, n, b, r, q, k).

            # Material: Suma el valor de la pieza al score de material.
            material_score += color_multiplier * piece_values[p_type]

            # Posición con PST (Piece-Square Table):
            val = 0 # Valor de la casilla según la PST.
            if p_type == "p":
                # Para peones, la tabla se invierte para las negras (7-r).
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
                # Determinar si es endgame para usar la tabla de rey de endgame.
                # Una heurística simple para endgame: si hay pocas piezas mayores (reinas y torres).
                num_major_pieces = 0
                for row_board in board.board:
                    for p in row_board:
                        if p != "--" and p[1] in ("q", "r"):
                            num_major_pieces += 1
                if num_major_pieces <= 4: # Arbitrario, se puede ajustar el umbral.
                    val = king_table_end[r][c] if piece[0] == "w" else king_table_end[7-r][c]
                else: # Si no es endgame, usa la tabla de medio juego.
                    val = king_table_mid[r][c] if piece[0] == "w" else king_table_mid[7-r][c]
            
            position_score += color_multiplier * val # Suma el valor posicional al score.

    # --- Movilidad ---
    # Se usa MoveGenerator para obtener los movimientos pseudo-legales de forma más eficiente.
    from IA.move_generator import MoveGenerator # Importa aquí para evitar importaciones circulares.
    # La movilidad se calcula como la diferencia entre el número de movimientos pseudo-legales de blancas y negras.
    mobility_score = len(MoveGenerator.generate_pseudo_legal_moves(board, "w")) - \
                     len(MoveGenerator.generate_pseudo_legal_moves(board, "b"))

    # --- Seguridad del Rey ---
    # Penalización más fuerte por estar en jaque.
    if board.is_check("w"): # Si el rey blanco está en jaque.
        king_safety_score -= 100 # Penalización para las blancas.
    if board.is_check("b"): # Si el rey negro está en jaque.
        king_safety_score += 100 # Bonificación para las blancas (penalización para las negras).

    # --- Estructura de Peones (Nueva heurística) ---
    # Penaliza peones doblados y aislados.
    for color in ["w", "b"]: # Itera para ambos colores.
        pawn_count_by_col = [0] * 8 # Cuenta los peones por columna.
        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r, c)
                if piece == color + "p": # Si es un peón del color actual.
                    pawn_count_by_col[c] += 1 # Incrementa el contador de la columna.
        
        for c in range(8):
            if pawn_count_by_col[c] > 1: # Peones doblados (más de un peón en la misma columna).
                pawn_structure_score += (-20 if color == "w" else 20) # Penaliza al color que tiene peones doblados.
            
            # Peones aislados (sin peones amigos en columnas adyacentes).
            if pawn_count_by_col[c] > 0: # Si hay un peón en esta columna.
                is_isolated = True
                if c > 0 and pawn_count_by_col[c-1] > 0: # Si hay un peón amigo a la izquierda.
                    is_isolated = False
                if c < 7 and pawn_count_by_col[c+1] > 0: # Si hay un peón amigo a la derecha.
                    is_isolated = False
                if is_isolated: # Si el peón está aislado.
                    pawn_structure_score += (-15 if color == "w" else 15) # Penaliza al color que tiene peones aislados.

    # --- Otras heurísticas ---
    # Par de alfiles: bonificación por tener dos alfiles.
    white_bishops = sum(1 for r in range(8) for c in range(8) if board.get_piece(r,c) == "wb")
    black_bishops = sum(1 for r in range(8) for c in range(8) if board.get_piece(r,c) == "bb")
    if white_bishops >= 2:
        other_score += 20 # Bonificación para las blancas.
    if black_bishops >= 2:
        other_score -= 20 # Penalización para las negras (bonificación para las blancas).

    # Control del centro (peones en d4, e4, d5, e5).
    center_squares = [(3,3), (3,4), (4,3), (4,4)] # Coordenadas de las casillas centrales.
    for r, c in center_squares:
        piece = board.get_piece(r, c)
        if piece == "wp": # Si hay un peón blanco en el centro.
            other_score += 10 # Bonificación para las blancas.
        elif piece == "bp": # Si hay un peón negro en el centro.
            other_score -= 10 # Penalización para las negras.

    # --- Fórmula final de evaluación ---
    # Combina todas las puntuaciones con sus pesos respectivos.
    score = (
        w_material * material_score +
        w_position * position_score +
        w_mobility * mobility_score +
        w_king_safety * king_safety_score +
        w_pawn_structure * pawn_structure_score +
        w_other * other_score
    )

    return score # Devuelve la puntuación total del tablero.



