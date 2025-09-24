# chessLogic/moves.py

def is_legal_move(chessboard, start_pos, end_pos, piece_type=None, pseudo_legal=False):
    """
    Verifica si un movimiento es legal geométricamente para una pieza específica.
    No verifica si el movimiento deja al rey en jaque.

    Args:
        chessboard (ChessBoard): La instancia del tablero de ajedrez.
        start_pos (tuple): Tupla (fila, columna) de la casilla de inicio.
        end_pos (tuple): Tupla (fila, columna) de la casilla de destino.
        piece_type (str, optional): Tipo de pieza a considerar (ej. "p", "r").
                                    Si es None, se usa el tipo de la pieza en start_pos.
        pseudo_legal (bool, optional): Si es True, no se validan los enroques especiales
                                       (solo el movimiento del rey de 1 casilla).
                                       Por defecto es False.

    Returns:
        bool: True si el movimiento es geométricamente legal, False en caso contrario.
    """
    from .rules import ChessRules # Importa ChessRules aquí para evitar importaciones circulares.

    board = chessboard.board # Accede al tablero de la instancia ChessBoard.
    start_row, start_col = start_pos # Desempaqueta las coordenadas de inicio.
    end_row, end_col = end_pos     # Desempaqueta las coordenadas de destino.

    piece = board[start_row][start_col] # Obtiene la pieza en la casilla de inicio.
    target = board[end_row][end_col]     # Obtiene la pieza en la casilla de destino.

    if piece == "--": # Si no hay pieza en la casilla de inicio, el movimiento es inválido.
        return False

    color = piece[0] # Color de la pieza que se mueve.
    p_type = piece[1] if piece_type is None else piece_type # Tipo de pieza.

    # Si la casilla de destino contiene una pieza del mismo color, el movimiento es inválido.
    if target != "--" and target[0] == color:
        return False

    # Lógica de movimiento para cada tipo de pieza.
    if p_type == "p": # Peón.
        # Verifica movimientos normales de peón y capturas.
        if _is_pawn_move(board, start_pos, end_pos, color):
            return True

        # --- EN PASSANT: validación estricta basada en start y end ---
        ep = chessboard.en_passant_square # Obtiene la casilla de en passant posible.
        if ep is not None: # Si hay una casilla de en passant.
            er, ec = ep # Coordenadas de la casilla de en passant.
            # El end_pos del movimiento debe coincidir con la casilla de en_passant.
            if (end_row, end_col) == (er, ec):
                direction = -1 if color == "w" else 1 # Dirección del peón.
                # Debe ser un movimiento diagonal de 1 casilla (columna adyacente y fila correcta).
                if (end_row - start_row) == direction and abs(end_col - start_col) == 1:
                    # Además, comprobamos que la casilla que contiene el peón "vulnerable"
                    # esté ocupada por un peón enemigo (en la misma fila que start, en la col end_col).
                    captured_r, captured_c = start_row, end_col
                    if 0 <= captured_r < 8 and 0 <= captured_c < 8: # Asegura que las coordenadas son válidas.
                        cap = board[captured_r][captured_c] # Pieza en la casilla del peón vulnerable.
                        # Debe ser un peón enemigo.
                        if cap != "--" and cap[1] == "p" and cap[0] != color:
                            return True
        return False # Si no es un movimiento de peón normal ni en passant, es inválido.
    elif p_type == "r": # Torre.
        return _is_rook_move(board, start_pos, end_pos)
    elif p_type == "n": # Caballo.
        return _is_knight_move(start_pos, end_pos)
    elif p_type == "b": # Alfil.
        return _is_bishop_move(board, start_pos, end_pos)
    elif p_type == "q": # Reina.
        return _is_queen_move(board, start_pos, end_pos)
    elif p_type == "k": # Rey.
        if _is_king_move(start_pos, end_pos): # Movimiento normal del rey.
            return True
        # Solo chequear enroque si NO es pseudo-legal (es decir, si estamos buscando movimientos legales completos).
        if not pseudo_legal:
            # Verifica si el enroque corto o largo es posible según las reglas de ChessRules.
            if (end_pos == (start_row, start_col + 2) and ChessRules.can_castle(chessboard, color, kingside=True)) or \
               (end_pos == (start_row, start_col - 2) and ChessRules.can_castle(chessboard, color, kingside=False)):
                return True
        return False # Si no es un movimiento de rey normal ni enroque, es inválido.

    return False # Si el tipo de pieza no es reconocido, el movimiento es inválido.

# ---------------------------
# Reglas geométricas de movimiento para cada pieza.
# Estas funciones solo verifican la trayectoria y si hay obstáculos, no jaques.
# ---------------------------

def _is_pawn_move(board, start, end, color):
    """
    Verifica si un movimiento de peón es geométricamente válido.
    """
    sr, sc = start # Fila y columna de inicio.
    er, ec = end   # Fila y columna de destino.
    direction = -1 if color == "w" else 1 # Dirección de avance del peón (blancas -1, negras +1).

    # Movimiento de un paso hacia adelante.
    if sc == ec and board[er][ec] == "--": # Si no cambia de columna y la casilla de destino está vacía.
        if er - sr == direction: # Si se mueve un paso en la dirección correcta.
            return True
        # Movimiento de dos pasos desde la posición inicial.
        if (sr == 6 and color == "w") or (sr == 1 and color == "b"): # Si está en su fila inicial.
            if er - sr == 2 * direction and board[sr + direction][sc] == "--": # Si se mueve dos pasos y la casilla intermedia está vacía.
                return True
    
    # Captura diagonal.
    if abs(ec - sc) == 1 and er - sr == direction: # Si se mueve diagonalmente un paso.
        if board[er][ec] != "--" and board[er][ec][0] != color: # Y hay una pieza enemiga en la casilla de destino.
            return True
    return False

def _is_rook_move(board, start, end):
    """
    Verifica si un movimiento de torre es geométricamente válido.
    """
    sr, sc = start
    er, ec = end
    if sr != er and sc != ec: # La torre solo se mueve en línea recta (horizontal o vertical).
        return False
    
    # Determina la dirección del movimiento.
    step_r = 0 if sr == er else (1 if er > sr else -1) # Paso en fila (0, 1 o -1).
    step_c = 0 if sc == ec else (1 if ec > sc else -1) # Paso en columna (0, 1 o -1).
    
    r, c = sr + step_r, sc + step_c # Empieza a verificar desde la casilla siguiente a la de inicio.
    while (r, c) != (er, ec): # Mientras no se llegue a la casilla de destino.
        if board[r][c] != "--": # Si hay una pieza en el camino, el movimiento es bloqueado.
            return False
        r += step_r # Avanza a la siguiente casilla en la trayectoria.
        c += step_c
    return True # Si no hay obstáculos, el movimiento es válido.

def _is_knight_move(start, end):
    """
    Verifica si un movimiento de caballo es geométricamente válido (forma de 'L').
    """
    sr, sc = start
    er, ec = end
    # Calcula la diferencia absoluta en filas y columnas.
    # Un movimiento de caballo es (2,1) o (1,2) en cualquier dirección.
    return (abs(sr - er), abs(sc - ec)) in [(2, 1), (1, 2)]

def _is_bishop_move(board, start, end):
    """
    Verifica si un movimiento de alfil es geométricamente válido.
    """
    sr, sc = start
    er, ec = end
    if abs(sr - er) != abs(sc - ec): # El alfil solo se mueve en diagonal (misma diferencia en filas y columnas).
        return False
    
    # Determina la dirección del movimiento diagonal.
    step_r = 1 if er > sr else -1
    step_c = 1 if ec > sc else -1
    
    r, c = sr + step_r, sc + step_c # Empieza a verificar desde la casilla siguiente a la de inicio.
    while (r, c) != (er, ec): # Mientras no se llegue a la casilla de destino.
        if board[r][c] != "--": # Si hay una pieza en el camino, el movimiento es bloqueado.
            return False
        r += step_r # Avanza a la siguiente casilla en la trayectoria.
        c += step_c
    return True # Si no hay obstáculos, el movimiento es válido.

def _is_queen_move(board, start, end):
    """
    Verifica si un movimiento de reina es geométricamente válido.
    La reina combina los movimientos de torre y alfil.
    """
    return _is_rook_move(board, start, end) or _is_bishop_move(board, start, end)

def _is_king_move(start, end):
    """
    Verifica si un movimiento de rey es geométricamente válido (una casilla en cualquier dirección).
    """
    sr, sc = start
    er, ec = end
    # El rey se mueve una casilla en cualquier dirección (horizontal, vertical o diagonal).
    return abs(sr - er) <= 1 and abs(sc - ec) <= 1


