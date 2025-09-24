class Move:
    def __init__(self, start_pos, end_pos, chessboard, promotion_choice="q"):
        """
        Inicializa un objeto Move.
        
        Args:
            start_pos (tuple): Tupla (fila, columna) de la casilla de inicio.
            end_pos (tuple): Tupla (fila, columna) de la casilla de destino.
            chessboard (ChessBoard): La instancia del tablero de ajedrez actual.
            promotion_choice (str, optional): La pieza a la que se promociona un peón ('q', 'r', 'b', 'n').
                                              Por defecto es 'q' (reina).
        """
        self.start_row, self.start_col = start_pos # Fila y columna de inicio.
        self.end_row, self.end_col = end_pos       # Fila y columna de destino.

        # Referencia al tablero actual para obtener información de las piezas.
        self.board = chessboard.board

        # Pieza que se mueve.
        self.piece_moved = self.board[self.start_row][self.start_col]
        # Pieza que se captura en la casilla de destino (puede ser "--" si no hay captura).
        self.piece_captured = self.board[self.end_row][self.end_col]

        # 🔹 Promoción de peón: True si la pieza movida es un peón y llega a la última fila.
        self.is_pawn_promotion = (
            self.piece_moved[1] == "p" and (self.end_row == 0 or self.end_row == 7)
        )
        self.promotion_choice = promotion_choice # La pieza elegida para la promoción.

        # 🔹 Enroque: True si la pieza movida es un rey y se mueve dos casillas horizontalmente.
        self.is_castling = (
            self.piece_moved[1] == "k" and abs(self.end_col - self.start_col) == 2
        )

        # 🔹 En passant: Inicialmente False, se verifica y actualiza si es necesario.
        self.is_en_passant = False
        # Si la pieza movida es un peón y cambia de columna sin capturar una pieza directamente.
        if self.piece_moved[1] == "p" and self.start_col != self.end_col:
            # Si la casilla de destino coincide con la casilla de en_passant_square del tablero.
            if chessboard.en_passant_square == (self.end_row, self.end_col):
                self.is_en_passant = True
                # La pieza capturada en en passant es el peón enemigo que fue "saltado".
                self.piece_captured = (
                    "bp" if self.piece_moved[0] == "w" else "wp" # Determina el color del peón capturado.
                )
        
        # Atributos para guardar el estado del tablero antes del movimiento,
        # necesarios para la función undo_move.
        self.prev_castling_rights = None
        self.prev_en_passant = None
        self.prev_white_king_pos = None
        self.prev_black_king_pos = None

    def __eq__(self, other):
        """
        Define cómo se comparan dos objetos Move para ver si son iguales.
        Útil para buscar movimientos específicos en listas.
        """
        if not isinstance(other, Move):
            return NotImplemented
        return (self.start_row == other.start_row and
                self.start_col == other.start_col and
                self.end_row == other.end_row and
                self.end_col == other.end_col and
                self.piece_moved == other.piece_moved and
                self.piece_captured == other.piece_captured and
                self.is_pawn_promotion == other.is_pawn_promotion and
                self.promotion_choice == other.promotion_choice and
                self.is_castling == other.is_castling and
                self.is_en_passant == other.is_en_passant)

    def __hash__(self):
        """
        Define el hash de un objeto Move, permitiendo que se use en conjuntos o como claves de diccionario.
        """
        return hash((self.start_row, self.start_col, self.end_row, self.end_col,
                     self.piece_moved, self.piece_captured, self.is_pawn_promotion,
                     self.promotion_choice, self.is_castling, self.is_en_passant))

    def __str__(self):
        """
        Representación en cadena del objeto Move, útil para depuración.
        """
        return f"{self.piece_moved} from ({self.start_row},{self.start_col}) to ({self.end_row},{self.end_col})"

