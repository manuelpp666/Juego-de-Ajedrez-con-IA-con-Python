# IA/move_generator.py
from chessLogic.moves import is_legal_move # Importa la función is_legal_move para verificar movimientos geométricos.
from chessLogic.rules import ChessRules # Importa ChessRules para verificar enroque.
from chessLogic.move import Move # Importa la clase Move para crear objetos de movimiento.

class MoveGenerator:
    """
    Clase estática para generar movimientos de ajedrez, tanto pseudo-legales como legales.
    """

    @staticmethod
    def generate_pseudo_legal_moves(chessboard, color):
        """
        Genera todos los movimientos pseudo-legales para un color dado de manera eficiente.
        Un movimiento pseudo-legal es aquel que cumple las reglas geométricas de la pieza,
        pero NO comprueba si deja al propio rey en jaque.
        
        Args:
            chessboard (ChessBoard): La instancia del tablero de ajedrez.
            color (str): El color del jugador ('w' para blancas o 'b' para negras).
            
        Returns:
            list: Una lista de tuplas, donde cada tupla representa un movimiento ((start_row, start_col), (end_row, end_col)).
        """
        moves = [] # Lista para almacenar los movimientos generados.
        board = chessboard.board # Accede al tablero.

        for r in range(8): # Itera sobre cada fila del tablero.
            for c in range(8): # Itera sobre cada columna del tablero.
                piece = board[r][c] # Obtiene la pieza en la casilla actual.
                if piece != "--" and piece[0] == color: # Si hay una pieza y es del color correcto.
                    p_type = piece[1] # Tipo de la pieza.
                    # Llama a la función específica para generar movimientos de cada tipo de pieza.
                    if p_type == "p":
                        moves.extend(MoveGenerator._get_pawn_moves(chessboard, (r, c), color))
                    elif p_type == "r":
                        moves.extend(MoveGenerator._get_rook_moves(chessboard, (r, c), color))
                    elif p_type == "n":
                        moves.extend(MoveGenerator._get_knight_moves(chessboard, (r, c), color))
                    elif p_type == "b":
                        moves.extend(MoveGenerator._get_bishop_moves(chessboard, (r, c), color))
                    elif p_type == "q":
                        moves.extend(MoveGenerator._get_queen_moves(chessboard, (r, c), color))
                    elif p_type == "k":
                        moves.extend(MoveGenerator._get_king_moves(chessboard, (r, c), color))
                        # Añadir enroque como pseudo-legal aquí para que minimax lo evalúe.
                        # Solo se verifica si el enroque es geométricamente posible y los derechos existen.
                        if ChessRules.can_castle(chessboard, color, kingside=True):
                            moves.append(((r, c), (r, c + 2))) # Movimiento de rey para enroque corto.
                        if ChessRules.can_castle(chessboard, color, kingside=False):
                            moves.append(((r, c), (r, c - 2))) # Movimiento de rey para enroque largo.
        return moves # Devuelve la lista de movimientos pseudo-legales.

    @staticmethod
    def _get_pawn_moves(chessboard, start_pos, color):
        """
        Genera los movimientos pseudo-legales para un peón.
        """
        moves = []
        sr, sc = start_pos # Fila y columna de inicio.
        direction = -1 if color == "w" else 1 # Dirección de avance del peón.
        
        # Movimiento de un paso hacia adelante.
        er, ec = sr + direction, sc # Casilla un paso adelante.
        if 0 <= er < 8 and chessboard.board[er][ec] == "--": # Si la casilla está dentro del tablero y vacía.
            moves.append((start_pos, (er, ec)))
            # Movimiento de dos pasos desde la posición inicial.
            if (sr == 6 and color == "w") or (sr == 1 and color == "b"): # Si el peón está en su fila inicial.
                er2 = sr + 2 * direction # Casilla dos pasos adelante.
                # Si la casilla dos pasos adelante y la casilla intermedia están vacías.
                if chessboard.board[er2][ec] == "--" and chessboard.board[sr + direction][sc] == "--":
                    moves.append((start_pos, (er2, ec)))
        
        # Capturas diagonales.
        for dc in [-1, 1]: # Para las dos diagonales.
            er, ec = sr + direction, sc + dc # Casilla de captura diagonal.
            if 0 <= er < 8 and 0 <= ec < 8: # Si la casilla está dentro del tablero.
                target_piece = chessboard.board[er][ec] # Pieza en la casilla de destino.
                if target_piece != "--" and target_piece[0] != color: # Si hay una pieza enemiga.
                    moves.append((start_pos, (er, ec)))
                # En passant: si la casilla de destino es la casilla de en passant posible.
                if chessboard.en_passant_square == (er, ec):
                    moves.append((start_pos, (er, ec)))
        return moves

    @staticmethod
    def _get_rook_moves(chessboard, start_pos, color):
        """
        Genera los movimientos pseudo-legales para una torre.
        """
        moves = []
        sr, sc = start_pos
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] # Direcciones: derecha, izquierda, abajo, arriba.
        for dr, dc in directions: # Itera sobre cada dirección.
            for i in range(1, 8): # Itera sobre la distancia máxima (hasta 7 casillas).
                er, ec = sr + dr * i, sc + dc * i # Calcula la casilla de destino.
                if not (0 <= er < 8 and 0 <= ec < 8): # Si se sale del tablero.
                    break
                target_piece = chessboard.board[er][ec] # Pieza en la casilla de destino.
                if target_piece == "--": # Si la casilla está vacía.
                    moves.append((start_pos, (er, ec)))
                elif target_piece[0] != color: # Si hay una pieza enemiga (captura).
                    moves.append((start_pos, (er, ec)))
                    break # La línea de visión se bloquea después de una captura.
                else: # Pieza del mismo color (bloquea la línea de visión).
                    break
        return moves

    @staticmethod
    def _get_knight_moves(chessboard, start_pos, color):
        """
        Genera los movimientos pseudo-legales para un caballo.
        """
        moves = []
        sr, sc = start_pos
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), # Todos los movimientos en 'L'.
                        (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in knight_moves: # Itera sobre cada movimiento de caballo.
            er, ec = sr + dr, sc + dc # Calcula la casilla de destino.
            if 0 <= er < 8 and 0 <= ec < 8: # Si la casilla está dentro del tablero.
                target_piece = chessboard.board[er][ec] # Pieza en la casilla de destino.
                if target_piece == "--" or target_piece[0] != color: # Si está vacía o hay una pieza enemiga.
                    moves.append((start_pos, (er, ec)))
        return moves

    @staticmethod
    def _get_bishop_moves(chessboard, start_pos, color):
        """
        Genera los movimientos pseudo-legales para un alfil.
        """
        moves = []
        sr, sc = start_pos
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)] # Direcciones diagonales.
        for dr, dc in directions: # Itera sobre cada dirección diagonal.
            for i in range(1, 8): # Itera sobre la distancia máxima.
                er, ec = sr + dr * i, sc + dc * i # Calcula la casilla de destino.
                if not (0 <= er < 8 and 0 <= ec < 8): # Si se sale del tablero.
                    break
                target_piece = chessboard.board[er][ec] # Pieza en la casilla de destino.
                if target_piece == "--": # Si la casilla está vacía.
                    moves.append((start_pos, (er, ec)))
                elif target_piece[0] != color: # Si hay una pieza enemiga (captura).
                    moves.append((start_pos, (er, ec)))
                    break # La línea de visión se bloquea.
                else: # Pieza del mismo color (bloquea la línea de visión).
                    break
        return moves

    @staticmethod
    def _get_queen_moves(chessboard, start_pos, color):
        """
        Genera los movimientos pseudo-legales para una reina.
        La reina combina los movimientos de torre y alfil.
        """
        # Combina los movimientos generados por las funciones de torre y alfil.
        return MoveGenerator._get_rook_moves(chessboard, start_pos, color) + \
               MoveGenerator._get_bishop_moves(chessboard, start_pos, color)

    @staticmethod
    def _get_king_moves(chessboard, start_pos, color):
        """
        Genera los movimientos pseudo-legales para un rey (movimientos de una casilla).
        """
        moves = []
        sr, sc = start_pos
        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), # Movimientos adyacentes (horizontal, vertical, diagonal).
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in king_moves: # Itera sobre cada movimiento posible del rey.
            er, ec = sr + dr, sc + dc # Calcula la casilla de destino.
            if 0 <= er < 8 and 0 <= ec < 8: # Si la casilla está dentro del tablero.
                target_piece = chessboard.board[er][ec] # Pieza en la casilla de destino.
                if target_piece == "--" or target_piece[0] != color: # Si está vacía o hay una pieza enemiga.
                    moves.append((start_pos, (er, ec)))
        return moves

    @staticmethod
    def generate_legal_moves(chessboard, color):
        """
        Genera movimientos legales reales para un color dado.
        - Parte de los movimientos pseudo-legales.
        - Hace y deshace cada movimiento en el tablero temporalmente.
        - Elimina los movimientos que dejan al propio rey en jaque.
        
        Args:
            chessboard (ChessBoard): La instancia del tablero de ajedrez.
            color (str): El color del jugador ('w' para blancas o 'b' para negras).
            
        Returns:
            list: Una lista de tuplas, donde cada tupla representa un movimiento ((start_row, start_col), (end_row, end_col)).
        """
        legal_moves = [] # Lista para almacenar los movimientos legales.
        # Obtiene todos los movimientos pseudo-legales.
        pseudo_moves = MoveGenerator.generate_pseudo_legal_moves(chessboard, color)

        for start, end in pseudo_moves: # Itera sobre cada movimiento pseudo-legal.
            # Crear un objeto Move para el movimiento actual.
            move = Move(start, end, chessboard)
            
            # Simular el movimiento en el tablero.
            chessboard.make_move(move)

            # Verificar si el rey del color actual está en jaque después del movimiento.
            if not ChessRules.is_in_check(chessboard, color):
                legal_moves.append((start, end)) # Si no está en jaque, el movimiento es legal.

            # Revertir el movimiento para restaurar el estado del tablero.
            chessboard.undo_move()

        return legal_moves # Devuelve la lista de movimientos legales.

    @staticmethod
    def has_any_legal_moves(chessboard, color):
        """
        Comprueba si un jugador tiene al menos un movimiento legal.
        Útil para detectar jaque mate o tablas por ahogado de forma más eficiente,
        ya que no necesita generar *todos* los movimientos legales, solo uno.
        
        Args:
            chessboard (ChessBoard): La instancia del tablero de ajedrez.
            color (str): El color del jugador ('w' para blancas o 'b' para negras).
            
        Returns:
            bool: True si el jugador tiene al menos un movimiento legal, False en caso contrario.
        """
        # Optimización: solo necesitamos encontrar UN movimiento legal.
        pseudo_moves = MoveGenerator.generate_pseudo_legal_moves(chessboard, color)

        for start, end in pseudo_moves: # Itera sobre cada movimiento pseudo-legal.
            move = Move(start, end, chessboard) # Crea un objeto Move.
            chessboard.make_move(move) # Simula el movimiento.
            if not ChessRules.is_in_check(chessboard, color): # Si el rey no está en jaque después del movimiento.
                chessboard.undo_move() # Revertir antes de retornar.
                return True # Se encontró al menos un movimiento legal.
            chessboard.undo_move() # Revertir el movimiento.
        return False # No se encontró ningún movimiento legal.


