# chessLogic/rules.py
from .utils import get_all_moves # Importa get_all_moves para usar en is_checkmate y is_stalemate.

class ChessRules:
    """
    Clase que contiene métodos estáticos para verificar reglas complejas del ajedrez,
    como enroque, en passant, jaque, jaque mate y ahogado.
    """

    @staticmethod
    def can_castle(chessboard, color, kingside=True):
        """
        Verifica si el enroque es posible para el color dado y el lado especificado.
        
        Args:
            chessboard (ChessBoard): La instancia del tablero de ajedrez.
            color (str): 'w' para blancas o 'b' para negras.
            kingside (bool, optional): True para enroque corto (lado del rey), False para enroque largo (lado de la reina).
                                       Por defecto es True.
                                       
        Returns:
            bool: True si el enroque es posible, False en caso contrario.
        """
        rights = chessboard.castling_rights # Obtiene los derechos de enroque actuales del tablero.
        king_pos = chessboard.white_king_pos if color == "w" else chessboard.black_king_pos # Posición actual del rey.
        row, col = king_pos # Desempaqueta la posición del rey.

        if color == "w": # Reglas para el enroque blanco.
            if kingside and rights["wK"] and king_pos == (7, 4): # Enroque corto blanco: rey en e1, derecho wK.
                # Casillas entre el rey y la torre deben estar vacías.
                if chessboard.board[7][5] == "--" and chessboard.board[7][6] == "--":
                    # Ninguna de las casillas por las que pasa el rey o donde termina debe estar atacada.
                    if not ChessRules.is_square_attacked(chessboard, (7, 4), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 5), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 6), "b"):
                        return True
            elif not kingside and rights["wQ"] and king_pos == (7, 4): # Enroque largo blanco: rey en e1, derecho wQ.
                # Casillas entre el rey y la torre deben estar vacías.
                if chessboard.board[7][1] == "--" and chessboard.board[7][2] == "--" and chessboard.board[7][3] == "--":
                    # Ninguna de las casillas por las que pasa el rey o donde termina debe estar atacada.
                    if not ChessRules.is_square_attacked(chessboard, (7, 4), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 3), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 2), "b"):
                        return True
        else: # Reglas para el enroque negro (análogas a las blancas).
            if kingside and rights["bK"] and king_pos == (0, 4): # Enroque corto negro.
                if chessboard.board[0][5] == "--" and chessboard.board[0][6] == "--":
                    if not ChessRules.is_square_attacked(chessboard, (0, 4), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 5), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 6), "w"):
                        return True
            elif not kingside and rights["bQ"] and king_pos == (0, 4): # Enroque largo negro.
                if chessboard.board[0][1] == "--" and chessboard.board[0][2] == "--" and chessboard.board[0][3] == "--":
                    if not ChessRules.is_square_attacked(chessboard, (0, 4), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 3), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 2), "w"):
                        return True
        return False # Si no se cumplen las condiciones, el enroque no es posible.

    @staticmethod
    def en_passant(chessboard, start, end):
        """
        Validación completa de en passant.
        
        Args:
            chessboard (ChessBoard): La instancia del tablero de ajedrez.
            start (tuple): Tupla (fila, columna) de la casilla de inicio del peón.
            end (tuple): Tupla (fila, columna) de la casilla de destino del peón.
            
        Returns:
            bool: True si el movimiento es un en passant válido, False en caso contrario.
        """
        sr, sc = start # Fila y columna de inicio.
        er, ec = end   # Fila y columna de destino.

        # Verificar límites del tablero.
        if not (0 <= sr < 8 and 0 <= sc < 8 and 0 <= er < 8 and 0 <= ec < 8):
            return False

        piece = chessboard.board[sr][sc] # Pieza en la casilla de inicio.
        if piece == "--" or piece[1] != "p": # Debe ser un peón.
            return False

        # Debe existir y coincidir la casilla de en_passant_square del tablero.
        if chessboard.en_passant_square is None:
            return False
        if (er, ec) != chessboard.en_passant_square: # La casilla de destino debe ser la casilla de en passant.
            return False

        # Dirección del movimiento del peón (blancas -1, negras +1).
        direction = -1 if piece[0] == "w" else 1

        # El movimiento debe ser un diagonal de 1 casilla en la dirección correcta.
        if (er - sr) != direction or abs(ec - sc) != 1:
            return False

        # La casilla del peón vulnerable está en la fila sr y columna ec.
        cap_r, cap_c = sr, ec
        if not (0 <= cap_r < 8 and 0 <= cap_c < 8): # Verificar límites.
            return False
        captured = chessboard.board[cap_r][cap_c] # Pieza en la casilla del peón vulnerable.
        # Debe haber un peón enemigo ahí.
        if captured == "--" or captured[1] != "p" or captured[0] == piece[0]:
            return False

        return True # Si todas las condiciones se cumplen, es un en passant válido.

    @staticmethod
    def promote(chessboard, row, col, new_piece="q"):
        """
        Realiza la promoción de un peón.
        
        Args:
            chessboard (ChessBoard): La instancia del tablero de ajedrez.
            row (int): La fila donde se encuentra el peón a promocionar.
            col (int): La columna donde se encuentra el peón a promocionar.
            new_piece (str, optional): El tipo de pieza a la que se promociona ('q', 'r', 'b', 'n').
                                       Por defecto es 'q' (reina).
        """
        piece = chessboard.board[row][col] # Obtiene la pieza en la casilla.
        if piece == "wp" and row == 0: # Si es un peón blanco en la fila 0.
            chessboard.board[row][col] = "w" + new_piece # Promociona a la nueva pieza blanca.
        elif piece == "bp" and row == 7: # Si es un peón negro en la fila 7.
            chessboard.board[row][col] = "b" + new_piece # Promociona a la nueva pieza negra.

    @staticmethod
    def is_square_attacked(chessboard, square, enemy_color):
        """
        Devuelve True si la casilla especificada está atacada por alguna pieza del color enemigo.
        
        Args:
            chessboard (ChessBoard): La instancia del tablero de ajedrez.
            square (tuple): Tupla (fila, columna) de la casilla a verificar.
            enemy_color (str): El color de las piezas atacantes ('w' o 'b').
            
        Returns:
            bool: True si la casilla está atacada, False en caso contrario.
        """
        board = chessboard.board # Accede al tablero.
        r, c = square # Desempaqueta las coordenadas de la casilla.

        # --- Peones ---
        # Define las direcciones de ataque de los peones según el color enemigo.
        if enemy_color == "w":  # Peones blancos atacan hacia abajo (hacia mayor fila).
            attack_dirs = [(1, -1), (1, 1)]
        else:  # Peones negros atacan hacia arriba (hacia menor fila).
            attack_dirs = [(-1, -1), (-1, 1)]

        for dr, dc in attack_dirs: # Itera sobre las direcciones de ataque del peón.
            nr, nc = r + dr, c + dc # Calcula la casilla atacada.
            if 0 <= nr < 8 and 0 <= nc < 8: # Si la casilla está dentro del tablero.
                if board[nr][nc] == enemy_color + "p": # Si hay un peón enemigo en esa casilla.
                    return True

        # --- Caballos ---
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), # Define todos los movimientos de caballo.
                        (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in knight_moves: # Itera sobre los movimientos de caballo.
            nr, nc = r + dr, c + dc # Calcula la casilla atacada.
            if 0 <= nr < 8 and 0 <= nc < 8: # Si la casilla está dentro del tablero.
                if board[nr][nc] == enemy_color + "n": # Si hay un caballo enemigo en esa casilla.
                    return True

        # --- Alfiles y Damas (diagonales) ---
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)] # Define las direcciones diagonales.
        for dr, dc in directions: # Itera sobre cada dirección diagonal.
            nr, nc = r, c # Empieza desde la casilla a verificar.
            while True:
                nr += dr # Avanza en la dirección diagonal.
                nc += dc
                if not (0 <= nr < 8 and 0 <= nc < 8): # Si se sale del tablero.
                    break
                if board[nr][nc] != "--": # Si encuentra una pieza.
                    # Si la pieza es un alfil o una reina enemiga, la casilla está atacada.
                    if board[nr][nc] in [enemy_color + "b", enemy_color + "q"]:
                        return True
                    break # Si encuentra cualquier pieza, la línea de visión está bloqueada.

        # --- Torres y Damas (líneas rectas) ---
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)] # Define las direcciones rectas.
        for dr, dc in directions: # Itera sobre cada dirección recta.
            nr, nc = r, c # Empieza desde la casilla a verificar.
            while True:
                nr += dr # Avanza en la dirección recta.
                nc += dc
                if not (0 <= nr < 8 and 0 <= nc < 8): # Si se sale del tablero.
                    break
                if board[nr][nc] != "--": # Si encuentra una pieza.
                    # Si la pieza es una torre o una reina enemiga, la casilla está atacada.
                    if board[nr][nc] in [enemy_color + "r", enemy_color + "q"]:
                        return True
                    break # Si encuentra cualquier pieza, la línea de visión está bloqueada.

        # --- Rey enemigo ---
        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), # Define todos los movimientos de rey.
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in king_moves: # Itera sobre los movimientos de rey.
            nr, nc = r + dr, c + dc # Calcula la casilla atacada.
            if 0 <= nr < 8 and 0 <= nc < 8: # Si la casilla está dentro del tablero.
                if board[nr][nc] == enemy_color + "k": # Si hay un rey enemigo en esa casilla.
                    return True

        return False # Si ninguna pieza enemiga ataca la casilla, devuelve False.

    @staticmethod
    def is_in_check(chessboard, color):
        """
        Verifica si el rey del color dado está en jaque.
        
        Args:
            chessboard (ChessBoard): La instancia del tablero de ajedrez.
            color (str): 'w' para blancas o 'b' para negras.
            
        Returns:
            bool: True si el rey está en jaque, False en caso contrario.
        """
        # Obtiene la posición del rey del color especificado.
        king_pos = chessboard.white_king_pos if color == "w" else chessboard.black_king_pos
        # Determina el color del enemigo.
        enemy_color = "b" if color == "w" else "w"
        # Llama a is_square_attacked para ver si la casilla del rey está atacada por el enemigo.
        return ChessRules.is_square_attacked(chessboard, king_pos, enemy_color)

    @staticmethod
    def is_special_move(chessboard, start, end):
        """
        Verifica si un movimiento es un movimiento especial (enroque o en passant).
        
        Args:
            chessboard (ChessBoard): La instancia del tablero de ajedrez.
            start (tuple): Tupla (fila, columna) de la casilla de inicio.
            end (tuple): Tupla (fila, columna) de la casilla de destino.
            
        Returns:
            bool: True si es un movimiento especial válido, False en caso contrario.
        """
        piece = chessboard.board[start[0]][start[1]] # Obtiene la pieza en la casilla de inicio.
        
        # Enroque: solo si la pieza es un rey y can_castle lo permite.
        if piece[1] == "k":
            if piece[0] == "w": # Rey blanco.
                if end == (7, 6) and ChessRules.can_castle(chessboard, "w", kingside=True): # Enroque corto blanco.
                    return True
                if end == (7, 2) and ChessRules.can_castle(chessboard, "w", kingside=False): # Enroque largo blanco.
                    return True
            else: # Rey negro.
                if end == (0, 6) and ChessRules.can_castle(chessboard, "b", kingside=True): # Enroque corto negro.
                    return True
                if end == (0, 2) and ChessRules.can_castle(chessboard, "b", kingside=False): # Enroque largo negro.
                    return True
        
        # En passant: solo si la pieza es un peón y en_passant lo valida.
        if piece[1] == "p" and ChessRules.en_passant(chessboard, start, end):
            return True
            
        return False # Si no es enroque ni en passant, no es un movimiento especial.

    @staticmethod
    def apply_special_move(chessboard, start, end):
        """
        Aplica un movimiento especial (enroque o en passant) al tablero.
        Nota: Esta función parece ser redundante o una versión anterior, ya que make_move en ChessBoard
              ya maneja los movimientos especiales. Podría ser eliminada o refactorizada.
        
        Args:
            chessboard (ChessBoard): La instancia del tablero de ajedrez.
            start (tuple): Tupla (fila, columna) de la casilla de inicio.
            end (tuple): Tupla (fila, columna) de la casilla de destino.
        """
        board = chessboard.board # Accede al tablero.
        piece = board[start[0]][start[1]] # Obtiene la pieza.

        # Enroque.
        if piece[1] == "k": # Si la pieza es un rey.
            if piece[0] == "w": # Rey blanco.
                if end == (7, 6):  # Enroque corto blanco.
                    board[7][6] = "wk" # Mueve el rey.
                    board[7][4] = "--" # Vacía la casilla original del rey.
                    board[7][5] = "wr" # Mueve la torre.
                    board[7][7] = "--" # Vacía la casilla original de la torre.
                    chessboard.white_king_pos = (7, 6) # Actualiza la posición del rey blanco.
                elif end == (7, 2):  # Enroque largo blanco.
                    board[7][2] = "wk"
                    board[7][4] = "--"
                    board[7][3] = "wr"
                    board[7][0] = "--"
                    chessboard.white_king_pos = (7, 2)
            else: # Rey negro.
                if end == (0, 6):  # Enroque corto negro.
                    board[0][6] = "bk"
                    board[0][4] = "--"
                    board[0][5] = "br"
                    board[0][7] = "--"
                    chessboard.black_king_pos = (0, 6)
                elif end == (0, 2):  # Enroque largo negro.
                    board[0][2] = "bk"
                    board[0][4] = "--"
                    board[0][3] = "br"
                    board[0][0] = "--"
                    chessboard.black_king_pos = (0, 2)

        # En passant.
        elif piece[1] == "p" and ChessRules.en_passant(chessboard, start, end): # Si es un peón y un en passant válido.
            direction = -1 if piece[0] == "w" else 1 # Dirección del peón.
            board[end[0]][end[1]] = piece # Mueve el peón que realiza el en passant.
            board[start[0]][start[1]] = "--" # Vacía la casilla original del peón.
            board[end[0] - direction][end[1]] = "--"  # Elimina el peón capturado.
            chessboard.en_passant_square = None # Resetea la casilla de en passant.

    @staticmethod
    def is_checkmate(board, color):
        """
        Verifica si el jugador del color dado está en jaque mate.
        
        Args:
            board (ChessBoard): La instancia del tablero de ajedrez.
            color (str): 'w' para blancas o 'b' para negras.
            
        Returns:
            bool: True si es jaque mate, False en caso contrario.
        """
        # 1. ¿El rey de este color está en jaque? Si no lo está, no puede ser jaque mate.
        if not ChessRules.is_in_check(board, color):
            return False

        # 2. ¿Hay algún movimiento legal que lo salve?
        # Se obtienen los movimientos legales para el color actual.
        moves = board.get_legal_moves(color)
        for move in moves: # Itera sobre cada movimiento legal.
            board.make_move(move) # Simula el movimiento.
            # Si después de hacer el movimiento, el rey ya no está en jaque.
            if not ChessRules.is_in_check(board, color):
                board.undo_move() # Deshace el movimiento.
                return False  # Encontró un movimiento que lo salva, por lo tanto, no es jaque mate.
            board.undo_move() # Deshace el movimiento.

        # Si no hay ningún movimiento que salve al rey, es jaque mate.
        return True

    @staticmethod
    def is_stalemate(board, color):
        """
        Verifica si el juego está en ahogado (stalemate) para el color dado.
        Ahogado: El jugador actual no tiene movimientos legales y no está en jaque.
        
        Args:
            board (ChessBoard): La instancia del tablero de ajedrez.
            color (str): 'w' para blancas o 'b' para negras.
            
        Returns:
            bool: True si es ahogado, False en caso contrario.
        """
        # 1. Si el rey está en jaque, no es ahogado (sería jaque mate si no hay movimientos).
        if ChessRules.is_in_check(board, color):
            return False

        # 2. Si tiene al menos un movimiento legal, no es ahogado.
        # Se obtienen los movimientos legales para el color actual.
        moves = board.get_legal_moves(color)
        for move in moves: # Itera sobre cada movimiento legal.
            board.make_move(move) # Simula el movimiento.
            # Si después de hacer el movimiento, el rey no está en jaque.
            if not ChessRules.is_in_check(board, color):
                board.undo_move() # Deshace el movimiento.
                return False # Encontró un movimiento legal que no deja al rey en jaque, no es ahogado.
            board.undo_move() # Deshace el movimiento.

        # 3. Si no hay movimiento legal y el rey no está en jaque, es ahogado.
        return True

