from . import moves
from . import rules
from .move import Move
from chessLogic.utils import get_all_moves
from chessLogic.rules import ChessRules

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
        self.en_passant_square = None   # 🔹 antes tenías en_passant_possible
        self.castling_rights = {"wK": True, "wQ": True, "bK": True, "bQ": True}
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)

        # 🔹 nuevo: log de movimientos
        self.move_log = []

        # 🔹 opcional: log de enroques para poder restaurarlos en undo
        self.castling_rights_log = [self.castling_rights.copy()]

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
    
    def make_move(self, move: Move):
        """Aplica un movimiento en el tablero con soporte de reglas"""
        # Guardar estado antes del movimiento
        move.prev_castling_rights = self.castling_rights.copy()
        move.prev_en_passant = self.en_passant_square
        move.prev_white_king_pos = self.white_king_pos
        move.prev_black_king_pos = self.black_king_pos

        # Movimiento normal
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved

        # 🔹 Actualizar posición del rey si se mueve
        if move.piece_moved[1] == "k":
            if move.piece_moved[0] == "w":
                self.white_king_pos = (move.end_row, move.end_col)
            else:
                self.black_king_pos = (move.end_row, move.end_col)

        # 🔹 Promoción
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + move.promotion_choice

        # 🔹 Enroque
        if move.is_castling:
            if move.end_col == 6:  # corto
                self.board[move.end_row][5] = self.board[move.end_row][7]
                self.board[move.end_row][7] = "--"
            else:  # largo
                self.board[move.end_row][3] = self.board[move.end_row][0]
                self.board[move.end_row][0] = "--"

        # 🔹 En passant
        self.en_passant_square = None
        if move.piece_moved[1] == "p" and abs(move.end_row - move.start_row) == 2:
            row = (move.start_row + move.end_row) // 2
            col = move.start_col
            if (col > 0 and self.board[move.end_row][col-1][0:1] == ('b' if move.piece_moved[0] == 'w' else 'w')) or \
            (col < 7 and self.board[move.end_row][col+1][0:1] == ('b' if move.piece_moved[0] == 'w' else 'w')):
                self.en_passant_square = (row, col)

        if move.is_en_passant:
            direction = 1 if move.piece_moved[0] == "b" else -1
            move.piece_captured = self.board[move.end_row - direction][move.end_col]
            self.board[move.end_row - direction][move.end_col] = "--"

        # 🔹 Actualizar derechos de enroque
        if move.piece_moved == "wk":
            self.castling_rights["wK"] = False
            self.castling_rights["wQ"] = False
        elif move.piece_moved == "bk":
            self.castling_rights["bK"] = False
            self.castling_rights["bQ"] = False
        elif move.piece_moved == "wr":
            if move.start_row == 7 and move.start_col == 0:
                self.castling_rights["wQ"] = False
            elif move.start_row == 7 and move.start_col == 7:
                self.castling_rights["wK"] = False
        elif move.piece_moved == "br":
            if move.start_row == 0 and move.start_col == 0:
                self.castling_rights["bQ"] = False
            elif move.start_row == 0 and move.start_col == 7:
                self.castling_rights["bK"] = False

        # Guardar log y cambiar turno
        self.move_log.append(move)
        self.turn = "b" if self.turn == "w" else "w"


    def undo_move(self):
        """Revierte el último movimiento"""
        if not self.move_log:
            return

        move = self.move_log.pop()

        # Restaurar tablero
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured

        # 🔹 Revertir promoción
        if move.is_pawn_promotion:
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured

        # 🔹 Revertir enroque
        if move.is_castling:
            if move.end_col == 6:  # corto
                self.board[move.end_row][7] = self.board[move.end_row][5]
                self.board[move.end_row][5] = "--"
            else:  # largo
                self.board[move.end_row][0] = self.board[move.end_row][3]
                self.board[move.end_row][3] = "--"

        # 🔹 Revertir en passant
        if move.is_en_passant:
            direction = 1 if move.piece_moved[0] == "b" else -1
            self.board[move.end_row - direction][move.end_col] = move.piece_captured
            self.board[move.end_row][move.end_col] = "--"

        # Restaurar posiciones de los reyes
        self.white_king_pos = move.prev_white_king_pos
        self.black_king_pos = move.prev_black_king_pos

        # Restaurar estados previos
        self.castling_rights = move.prev_castling_rights
        self.en_passant_square = move.prev_en_passant

        # Revertir turno
        self.turn = "b" if self.turn == "w" else "w"



    


    def is_game_over(self):
        if self.is_checkmate("w") or self.is_checkmate("b"):
            return True
        if self.is_stalemate("w") or self.is_stalemate("b"):
            return True
        return False
    
    def get_legal_moves(self, color=None):
        if color is None:
            color = self.turn  # por defecto usa el turno actual

        legal_moves = []
        
        pseudo_moves = get_all_moves(self, color, pseudo_legal=False)

        # Filtrar los movimientos que dejen al rey en jaque
        for move in pseudo_moves:
            self.make_move(Move(move[0], move[1], self))
            if not ChessRules.is_in_check(self, color):
                legal_moves.append(Move(move[0], move[1], self))
            self.undo_move()

        return legal_moves

    
