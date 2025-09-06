from . import moves
from . import rules

class ChessBoard:
    def __init__(self):
        self.board = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
            ["bp"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["wp"] * 8,
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
        ]
        self.turn = "w"
        self.en_passant_possible = None
        self.castling_rights = {"wK": True, "wQ": True, "bK": True, "bQ": True}
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)

    def get_piece(self, row, col):
        return self.board[row][col]

    def is_valid_move(self, start_pos, end_pos, color_override=None):
        start_row, start_col = start_pos
        piece = self.board[start_row][start_col]

        # Color que se usa para validar (puede forzarse con override)
        color = color_override if color_override else self.turn

        if piece == "--" or piece[0] != color:
            return False

        # Validar reglas geométricas
        if not moves.is_legal_move(self, start_pos, end_pos):
            if not rules.ChessRules.is_special_move(self, start_pos, end_pos):
                return False

        # Simular movimiento para verificar jaque
        temp_piece = self.board[end_pos[0]][end_pos[1]]
        self.board[end_pos[0]][end_pos[1]] = piece
        self.board[start_row][start_col] = "--"

        # Actualizar posición temporal del rey
        old_king_pos = None
        if piece[1] == "k":
            old_king_pos = self.white_king_pos if piece[0] == "w" else self.black_king_pos
            if piece[0] == "w":
                self.white_king_pos = (end_pos[0], end_pos[1])
            else:
                self.black_king_pos = (end_pos[0], end_pos[1])

        king_in_check = rules.ChessRules.is_in_check(self, color)

        # Revertir
        self.board[start_row][start_col] = piece
        self.board[end_pos[0]][end_pos[1]] = temp_piece
        if old_king_pos:
            if piece[0] == "w":
                self.white_king_pos = old_king_pos
            else:
                self.black_king_pos = old_king_pos

        return not king_in_check


    def move_piece(self, start_pos, end_pos, promote_to="q"):
        if not self.is_valid_move(start_pos, end_pos):
            return False

        start_row, start_col = start_pos
        end_row, end_col = end_pos
        piece = self.board[start_row][start_col]

        # Ejecutar movimientos especiales si aplica
        if rules.ChessRules.is_special_move(self, start_pos, end_pos):
            rules.ChessRules.apply_special_move(self, start_pos, end_pos)
        else:
            # Movimiento normal
            self.board[end_row][end_col] = piece
            self.board[start_row][start_col] = "--"

        # Actualizar posición del rey
        if piece[1] == "k":
            if piece[0] == "w":
                self.white_king_pos = (end_row, end_col)
            else:
                self.black_king_pos = (end_row, end_col)

        # Promoción de peón
        if piece[1] == "p" and (end_row == 0 or end_row == 7):
            if promote_to in ["q", "r", "b", "n"]:
                self.board[end_row][end_col] = piece[0] + promote_to
            else:
                self.board[end_row][end_col] = piece[0] + "q"  # por defecto

        # Actualizar captura al paso
        self.en_passant_possible = None
        if piece[1] == "p" and abs(end_row - start_row) == 2:
            self.en_passant_possible = ((start_row + end_row)//2, start_col)

        # Cambiar turno
        self.turn = "b" if self.turn == "w" else "w"
        return True
    
    def is_check(self, color):
        """
        Verifica si el rey del color dado está en jaque.
        """
        return rules.ChessRules.is_in_check(self, color)
    
    def has_valid_moves(self, color):
        from .utils import get_all_moves
        # obtener todos los movimientos pseudo-legales del color
        moves = get_all_moves(self, color, pseudo_legal=True)

        # probar si al menos uno no deja al rey en jaque
        for start, end in moves:
            start_piece = self.board[start[0]][start[1]]
            captured = self.board[end[0]][end[1]]

            # simular
            self.board[end[0]][end[1]] = start_piece
            self.board[start[0]][start[1]] = "--"

            old_king_pos = None
            if start_piece[1] == "k":
                old_king_pos = self.white_king_pos if color == "w" else self.black_king_pos
                if color == "w":
                    self.white_king_pos = end
                else:
                    self.black_king_pos = end

            in_check = rules.ChessRules.is_in_check(self, color)

            # revertir
            self.board[start[0]][start[1]] = start_piece
            self.board[end[0]][end[1]] = captured
            if old_king_pos:
                if color == "w":
                    self.white_king_pos = old_king_pos
                else:
                    self.black_king_pos = old_king_pos

            if not in_check:
                return True

        return False
    
    def is_checkmate(self, color):
        """
        Devuelve True si el jugador está en jaque mate.
        """
        if self.is_check(color) and not self.has_valid_moves(color):
            return True
        return False
    
    
    
    
