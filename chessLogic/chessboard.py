from . import moves # Importa el módulo 'moves' que contiene las reglas geométricas de movimiento.
from . import rules # Importa el módulo 'rules' que contiene reglas de ajedrez como jaque, enroque, etc.
from .move import Move # Importa la clase 'Move' para representar un movimiento.
from chessLogic.utils import get_all_moves # Importa la función para obtener todos los movimientos posibles.
from chessLogic.rules import ChessRules # Importa la clase ChessRules para acceder a sus métodos estáticos.

class ChessBoard:
    def __init__(self):
        # Inicializa el tablero de ajedrez con la configuración inicial de las piezas.
        # Cada elemento es una cadena de 2 caracteres: color (w/b) + tipo de pieza (r/n/b/q/k/p).
        # "--" representa una casilla vacía.
        self.board = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"], # Fila 0: Piezas negras
            ["bp"] * 8,                                     # Fila 1: Peones negros
            ["--"] * 8,                                     # Fila 2: Vacía
            ["--"] * 8,                                     # Fila 3: Vacía
            ["--"] * 8,                                     # Fila 4: Vacía
            ["--"] * 8,                                     # Fila 5: Vacía
            ["wp"] * 8,                                     # Fila 6: Peones blancos
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]  # Fila 7: Piezas blancas
        ]
        self.turn = "w" # El turno inicial es para las blancas ('w').
        self.en_passant_square = None   # 🔹 Casilla donde es posible un en passant. Se actualiza después de un movimiento de peón doble.
        # Derechos de enroque para cada rey y torre. True si es posible, False si ya se movió la pieza.
        self.castling_rights = {"wK": True, "wQ": True, "bK": True, "bQ": True}
        self.white_king_pos = (7, 4) # Posición inicial del rey blanco.
        self.black_king_pos = (0, 4) # Posición inicial del rey negro.

        # 🔹 nuevo: log de movimientos para poder deshacerlos.
        self.move_log = []

        # 🔹 opcional: log de derechos de enroque para poder restaurarlos en undo.
        self.castling_rights_log = [self.castling_rights.copy()]

    def get_piece(self, row, col):
        """
        Devuelve la pieza en la casilla especificada (row, col).
        """
        return self.board[row][col]

    def is_valid_move(self, start_pos, end_pos, color_override=None):
        """
        Verifica si un movimiento es legal, considerando las reglas del ajedrez y si deja al rey en jaque.
        
        Args:
            start_pos (tuple): Tupla (fila, columna) de la casilla de inicio.
            end_pos (tuple): Tupla (fila, columna) de la casilla de destino.
            color_override (str, optional): Permite forzar la validación para un color específico.
                                            Útil para la IA. Por defecto, usa el turno actual.
        
        Returns:
            bool: True si el movimiento es válido, False en caso contrario.
        """
        start_row, start_col = start_pos
        piece = self.board[start_row][start_col]

        # Color que se usa para validar (puede forzarse con override).
        color = color_override if color_override else self.turn

        # Si no hay pieza en la casilla de inicio o la pieza no es del color correcto, el movimiento es inválido.
        if piece == "--" or piece[0] != color:
            return False

        # Validar reglas geométricas (cómo se mueve la pieza) y movimientos especiales (enroque, en passant).
        # Si no es un movimiento geométricamente legal y tampoco es un movimiento especial, es inválido.
        if not moves.is_legal_move(self, start_pos, end_pos):
            if not rules.ChessRules.is_special_move(self, start_pos, end_pos):
                return False

        # --- Simular el movimiento para verificar si el rey queda en jaque ---
        temp_piece = self.board[end_pos[0]][end_pos[1]] # Guarda la pieza en la casilla de destino (por si es una captura).
        self.board[end_pos[0]][end_pos[1]] = piece      # Mueve la pieza a la casilla de destino.
        self.board[start_row][start_col] = "--"         # Vacía la casilla de inicio.

        # Actualizar temporalmente la posición del rey si la pieza movida es un rey.
        old_king_pos = None
        if piece[1] == "k": # Si la pieza movida es un rey.
            old_king_pos = self.white_king_pos if piece[0] == "w" else self.black_king_pos # Guarda la posición actual del rey.
            if piece[0] == "w":
                self.white_king_pos = (end_pos[0], end_pos[1]) # Actualiza la posición del rey blanco.
            else:
                self.black_king_pos = (end_pos[0], end_pos[1]) # Actualiza la posición del rey negro.

        # Verifica si el rey del color actual está en jaque después del movimiento simulado.
        king_in_check = rules.ChessRules.is_in_check(self, color)

        # --- Revertir el movimiento simulado para restaurar el estado del tablero ---
        self.board[start_row][start_col] = piece        # Devuelve la pieza a su casilla de inicio.
        self.board[end_pos[0]][end_pos[1]] = temp_piece # Restaura la pieza capturada (o vacía la casilla).
        if old_king_pos: # Si la posición del rey fue actualizada temporalmente.
            if piece[0] == "w":
                self.white_king_pos = old_king_pos # Restaura la posición original del rey blanco.
            else:
                self.black_king_pos = old_king_pos # Restaura la posición original del rey negro.

        # El movimiento es válido si el rey no está en jaque después de realizarlo.
        return not king_in_check

    
    def is_check(self, color):
        """
        Verifica si el rey del color dado está en jaque.
        
        Args:
            color (str): 'w' para blancas o 'b' para negras.
            
        Returns:
            bool: True si el rey está en jaque, False en caso contrario.
        """
        return rules.ChessRules.is_in_check(self, color)
    
    def has_valid_moves(self, color):
        """
        Verifica si el jugador del color dado tiene al menos un movimiento legal.
        Esto es crucial para detectar jaque mate o ahogado.
        
        Args:
            color (str): 'w' para blancas o 'b' para negras.
            
        Returns:
            bool: True si tiene movimientos válidos, False en caso contrario.
        """
        from .utils import get_all_moves # Importa get_all_moves aquí para evitar importaciones circulares.
        # Obtener todos los movimientos pseudo-legales del color (sin verificar jaque).
        moves = get_all_moves(self, color, pseudo_legal=True)

        # Probar si al menos uno de estos movimientos no deja al rey en jaque.
        for start, end in moves:
            start_piece = self.board[start[0]][start[1]] # Pieza en la casilla de inicio.
            captured = self.board[end[0]][end[1]]       # Pieza en la casilla de destino (posible captura).

            # Simular el movimiento.
            self.board[end[0]][end[1]] = start_piece # Mueve la pieza.
            self.board[start[0]][start[1]] = "--"    # Vacía la casilla de inicio.

            old_king_pos = None
            if start_piece[1] == "k": # Si la pieza movida es un rey.
                old_king_pos = self.white_king_pos if color == "w" else self.black_king_pos # Guarda la posición actual del rey.
                if color == "w":
                    self.white_king_pos = end # Actualiza la posición del rey blanco.
                else:
                    self.black_king_pos = end # Actualiza la posición del rey negro.

            # Verifica si el rey está en jaque después del movimiento simulado.
            in_check = rules.ChessRules.is_in_check(self, color)

            # Revertir el movimiento simulado.
            self.board[start[0]][start[1]] = start_piece # Restaura la pieza a su posición original.
            self.board[end[0]][end[1]] = captured       # Restaura la pieza capturada (o vacía la casilla).
            if old_king_pos: # Si la posición del rey fue actualizada temporalmente.
                if color == "w":
                    self.white_king_pos = old_king_pos # Restaura la posición original del rey blanco.
                else:
                    self.black_king_pos = old_king_pos # Restaura la posición original del rey negro.

            if not in_check: # Si se encuentra un movimiento que no deja al rey en jaque.
                return True # El jugador tiene movimientos válidos.

        return False # No se encontraron movimientos válidos.
    
    def is_checkmate(self, color):
        """
        Devuelve True si el jugador del color dado está en jaque mate.
        Un jugador está en jaque mate si está en jaque y no tiene movimientos legales.
        
        Args:
            color (str): 'w' para blancas o 'b' para negras.
            
        Returns:
            bool: True si es jaque mate, False en caso contrario.
        """
        if self.is_check(color) and not self.has_valid_moves(color):
            return True
        return False
    
    def make_move(self, move: Move):
        """
        Aplica un movimiento en el tablero con soporte de reglas especiales.
        
        Args:
            move (Move): Objeto Move que describe el movimiento a realizar.
        """
        # Guardar estado antes del movimiento para poder deshacerlo.
        move.prev_castling_rights = self.castling_rights.copy() # Guarda una copia de los derechos de enroque.
        move.prev_en_passant = self.en_passant_square # Guarda la casilla de en passant.
        move.prev_white_king_pos = self.white_king_pos # Guarda la posición del rey blanco.
        move.prev_black_king_pos = self.black_king_pos # Guarda la posición del rey negro.

        # Movimiento normal: mueve la pieza de la casilla de inicio a la de destino.
        self.board[move.start_row][move.start_col] = "--" # Vacía la casilla de inicio.
        self.board[move.end_row][move.end_col] = move.piece_moved # Coloca la pieza movida en la casilla de destino.

        # 🔹 Actualizar posición del rey si se mueve.
        if move.piece_moved[1] == "k": # Si la pieza movida es un rey.
            if move.piece_moved[0] == "w":
                self.white_king_pos = (move.end_row, move.end_col) # Actualiza la posición del rey blanco.
            else:
                self.black_king_pos = (move.end_row, move.end_col) # Actualiza la posición del rey negro.

        # 🔹 Promoción de peón.
        if move.is_pawn_promotion:
            # Reemplaza el peón en la última fila con la pieza elegida para la promoción.
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + move.promotion_choice

        # 🔹 Enroque.
        if move.is_castling:
            if move.end_col == 6:  # Enroque corto (lado del rey).
                self.board[move.end_row][5] = self.board[move.end_row][7] # Mueve la torre.
                self.board[move.end_row][7] = "--" # Vacía la casilla original de la torre.
            else:  # Enroque largo (lado de la reina).
                self.board[move.end_row][3] = self.board[move.end_row][0] # Mueve la torre.
                self.board[move.end_row][0] = "--" # Vacía la casilla original de la torre.

        # 🔹 En passant: Actualiza la casilla en_passant_square.
        self.en_passant_square = None # Por defecto, no hay casilla de en passant después de un movimiento.
        # Si un peón se mueve dos casillas.
        if move.piece_moved[1] == "p" and abs(move.end_row - move.start_row) == 2:
            row = (move.start_row + move.end_row) // 2 # La casilla de en passant es la que el peón "saltó".
            col = move.start_col
            # Verifica si hay peones enemigos adyacentes que puedan realizar en passant.
            if (col > 0 and self.board[move.end_row][col-1][0:1] == ('b' if move.piece_moved[0] == 'w' else 'w')) or \
            (col < 7 and self.board[move.end_row][col+1][0:1] == ('b' if move.piece_moved[0] == 'w' else 'w')):
                self.en_passant_square = (row, col) # Establece la casilla de en passant.

        if move.is_en_passant:
            # Si el movimiento es un en passant, elimina el peón capturado.
            direction = 1 if move.piece_moved[0] == "b" else -1 # Dirección del movimiento del peón.
            move.piece_captured = self.board[move.end_row - direction][move.end_col] # Guarda el peón capturado.
            self.board[move.end_row - direction][move.end_col] = "--" # Elimina el peón capturado.

        # 🔹 Actualizar derechos de enroque.
        # Si el rey se mueve, pierde ambos derechos de enroque.
        if move.piece_moved == "wk":
            self.castling_rights["wK"] = False
            self.castling_rights["wQ"] = False
        elif move.piece_moved == "bk":
            self.castling_rights["bK"] = False
            self.castling_rights["bQ"] = False
        # Si una torre se mueve de su posición inicial, pierde el derecho de enroque de ese lado.
        elif move.piece_moved == "wr":
            if move.start_row == 7 and move.start_col == 0: # Torre blanca de la reina.
                self.castling_rights["wQ"] = False
            elif move.start_row == 7 and move.start_col == 7: # Torre blanca del rey.
                self.castling_rights["wK"] = False
        elif move.piece_moved == "br":
            if move.start_row == 0 and move.start_col == 0: # Torre negra de la reina.
                self.castling_rights["bQ"] = False
            elif move.start_row == 0 and move.start_col == 7: # Torre negra del rey.
                self.castling_rights["bK"] = False

        # Guardar el movimiento en el log y cambiar el turno.
        self.move_log.append(move) # Añade el objeto Move al historial.
        self.turn = "b" if self.turn == "w" else "w" # Cambia el turno al otro color.


    def undo_move(self):
        """
        Revierte el último movimiento realizado en el tablero.
        """
        if not self.move_log: # Si no hay movimientos en el log, no hay nada que deshacer.
            return

        move = self.move_log.pop() # Obtiene el último movimiento del log.

        # Restaurar el tablero a su estado anterior al movimiento.
        self.board[move.start_row][move.start_col] = move.piece_moved # Devuelve la pieza movida a su origen.
        self.board[move.end_row][move.end_col] = move.piece_captured # Restaura la pieza capturada (o vacía la casilla).

        # 🔹 Revertir promoción de peón.
        if move.is_pawn_promotion:
            # Si hubo promoción, la pieza en la casilla de inicio debe volver a ser un peón.
            self.board[move.start_row][move.start_col] = move.piece_moved
            # La casilla de destino debe restaurar la pieza que estaba allí (o estar vacía).
            self.board[move.end_row][move.end_col] = move.piece_captured

        # 🔹 Revertir enroque.
        if move.is_castling:
            if move.end_col == 6:  # Enroque corto.
                self.board[move.end_row][7] = self.board[move.end_row][5] # Devuelve la torre a su posición original.
                self.board[move.end_row][5] = "--" # Vacía la casilla donde estaba la torre después del enroque.
            else:  # Enroque largo.
                self.board[move.end_row][0] = self.board[move.end_row][3] # Devuelve la torre a su posición original.
                self.board[move.end_row][3] = "--" # Vacía la casilla donde estaba la torre después del enroque.

        # 🔹 Revertir en passant.
        if move.is_en_passant:
            # Si fue un en passant, el peón capturado debe ser restaurado.
            direction = 1 if move.piece_moved[0] == "b" else -1 # Dirección del movimiento del peón.
            self.board[move.end_row - direction][move.end_col] = move.piece_captured # Restaura el peón capturado.
            self.board[move.end_row][move.end_col] = "--" # Vacía la casilla de destino del peón que realizó el en passant.

        # Restaurar posiciones de los reyes.
        self.white_king_pos = move.prev_white_king_pos # Restaura la posición del rey blanco.
        self.black_king_pos = move.prev_black_king_pos # Restaura la posición del rey negro.

        # Restaurar estados previos de derechos de enroque y en passant.
        self.castling_rights = move.prev_castling_rights # Restaura los derechos de enroque.
        self.en_passant_square = move.prev_en_passant # Restaura la casilla de en passant.

        # Revertir el turno.
        self.turn = "b" if self.turn == "w" else "w" # Cambia el turno de nuevo al color anterior.


    def is_game_over(self):
        """
        Verifica si el juego ha terminado por jaque mate o ahogado.
        
        Returns:
            bool: True si el juego ha terminado, False en caso contrario.
        """
        if self.is_checkmate("w") or self.is_checkmate("b"): # Si hay jaque mate para blancas o negras.
            return True
        if self.is_stalemate("w") or self.is_stalemate("b"): # Si hay ahogado para blancas o negras.
            return True
        return False
    
    def get_legal_moves(self, color=None):
        """
        Genera y devuelve una lista de todos los movimientos legales para el color especificado.
        Un movimiento es legal si no deja al propio rey en jaque.
        
        Args:
            color (str, optional): El color del jugador para el que se buscan movimientos.
                                   Por defecto, usa el turno actual.
                                   
        Returns:
            list: Una lista de objetos Move que representan los movimientos legales.
        """
        if color is None:
            color = self.turn  # Por defecto, usa el turno actual.

        legal_moves = [] # Lista para almacenar los movimientos legales.
        
        # Obtiene todos los movimientos pseudo-legales (que cumplen las reglas geométricas).
        pseudo_moves = get_all_moves(self, color, pseudo_legal=False)

        # Filtrar los movimientos que dejen al rey en jaque.
        for move_tuple in pseudo_moves:
            # Crea un objeto Move a partir de la tupla (start_pos, end_pos).
            move = Move(move_tuple[0], move_tuple[1], self)
            
            self.make_move(move) # Simula el movimiento en el tablero.
            # Si después de hacer el movimiento, el rey del color actual NO está en jaque.
            if not ChessRules.is_in_check(self, color):
                legal_moves.append(move) # El movimiento es legal, añádelo a la lista.
            self.undo_move() # Deshace el movimiento para restaurar el tablero.

        return legal_moves # Devuelve la lista de movimientos legales.

    def is_stalemate(self, current_turn):
        """
        Verifica si el juego está en ahogado (stalemate) para el turno actual.
        Ahogado: El jugador actual no tiene movimientos legales y no está en jaque.
        
        Args:
            current_turn (str): 'w' para blancas o 'b' para negras.
        
        Returns:
            bool: True si es ahogado, False otherwise.
        """
        # Verificar si el jugador actual no está en jaque. Si lo está, no puede ser ahogado (sería jaque mate si no hay movimientos).
        if self.is_check(current_turn):
            return False
        
        # Generar todos los movimientos legales para el jugador actual.
        legal_moves = self.get_legal_moves(current_turn)
        
        # Si no hay movimientos legales y no está en jaque, es ahogado.
        return len(legal_moves) == 0



    
