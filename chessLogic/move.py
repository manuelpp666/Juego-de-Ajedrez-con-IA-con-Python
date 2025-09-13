class Move:
    def __init__(self, start_pos, end_pos, chessboard, promotion_choice="q"):
        self.start_row, self.start_col = start_pos
        self.end_row, self.end_col = end_pos

        # tablero actual
        self.board = chessboard.board

        self.piece_moved = self.board[self.start_row][self.start_col]
        self.piece_captured = self.board[self.end_row][self.end_col]

        # 🔹 Promoción de peón
        self.is_pawn_promotion = (
            self.piece_moved[1] == "p" and (self.end_row == 0 or self.end_row == 7)
        )
        self.promotion_choice = promotion_choice

        # 🔹 Enroque
        self.is_castling = (
            self.piece_moved[1] == "k" and abs(self.end_col - self.start_col) == 2
        )

        # 🔹 En passant
        self.is_en_passant = False
        if self.piece_moved[1] == "p" and self.start_col != self.end_col:
            # Si la casilla de destino coincide con en_passant_square del tablero
            if chessboard.en_passant_square == (self.end_row, self.end_col):
                self.is_en_passant = True
                # capturamos el peón correcto al pasar
                self.piece_captured = (
                    "bp" if self.piece_moved[0] == "w" else "wp"
                )
