class Move:
    def __init__(self, start_pos, end_pos, board, promotion_choice="q"):
        self.start_row, self.start_col = start_pos
        self.end_row, self.end_col = end_pos

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.is_pawn_promotion = (
            self.piece_moved[1] == "p" and (self.end_row == 0 or self.end_row == 7)
        )
        self.promotion_choice = promotion_choice

        self.is_castling = (
            self.piece_moved[1] == "k" and abs(self.end_col - self.start_col) == 2
        )

        self.is_en_passant = (
            self.piece_moved[1] == "p" and self.piece_captured == "--" and self.start_col != self.end_col
        )

    def __repr__(self):
        return f"{self.piece_moved}@({self.start_row},{self.start_col})->({self.end_row},{self.end_col})"
    
    
