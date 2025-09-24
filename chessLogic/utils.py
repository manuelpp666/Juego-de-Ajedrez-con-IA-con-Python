# chessLogic/utils.py

def get_all_moves(chessboard, color, pseudo_legal=False):
    """
    Genera una lista de todos los movimientos posibles para un color dado en el tablero.
    
    Args:
        chessboard (ChessBoard): La instancia del tablero de ajedrez.
        color (str): El color del jugador ('w' para blancas o 'b' para negras).
        pseudo_legal (bool, optional): Si es True, genera movimientos pseudo-legales (solo reglas geométricas,
                                       sin verificar si el rey queda en jaque).
                                       Si es False, genera movimientos legales completos (verificando jaque).
                                       Por defecto es False.
                                       
    Returns:
        list: Una lista de tuplas, donde cada tupla representa un movimiento ((start_row, start_col), (end_row, end_col)).
    """
    from .moves import is_legal_move # Importa is_legal_move aquí para evitar importaciones circulares.
    

    moves_list = [] # Lista para almacenar los movimientos generados.
    board = chessboard.board # Accede al tablero de la instancia ChessBoard.

    for r in range(8): # Itera sobre cada fila del tablero.
        for c in range(8): # Itera sobre cada columna del tablero.
            piece = board[r][c] # Obtiene la pieza en la casilla actual.
            # Si hay una pieza en la casilla y es del color del jugador actual.
            if piece != "--" and piece[0] == color:
                for er in range(8): # Itera sobre todas las posibles filas de destino.
                    for ec in range(8): # Itera sobre todas las posibles columnas de destino.
                        if pseudo_legal:
                            # Movimientos pseudo-legales: solo reglas geométricas.
                            # Llama a is_legal_move con pseudo_legal=True para ignorar la verificación de enroque completo.
                            if is_legal_move(chessboard, (r, c), (er, ec), pseudo_legal=True):
                                moves_list.append(((r, c), (er, ec))) # Añade el movimiento a la lista.
                        else:
                            # Movimientos legales completos (incluye enroque completo y en passant).
                            # Llama a is_legal_move con pseudo_legal=False.
                            if is_legal_move(chessboard, (r, c), (er, ec), pseudo_legal=False):
                                moves_list.append(((r, c), (er, ec))) # Añade el movimiento a la lista.
    return moves_list # Devuelve la lista de movimientos.


