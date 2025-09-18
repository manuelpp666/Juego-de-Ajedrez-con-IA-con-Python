# chessLogic/rules.py
from .utils import get_all_moves

class ChessRules:

    @staticmethod
    def can_castle(chessboard, color, kingside=True):
        rights = chessboard.castling_rights
        king_pos = chessboard.white_king_pos if color == "w" else chessboard.black_king_pos
        row, col = king_pos

        if color == "w":
            if kingside and rights["wK"] and king_pos == (7, 4):
                if chessboard.board[7][5] == "--" and chessboard.board[7][6] == "--":
                    if not ChessRules.is_square_attacked(chessboard, (7, 4), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 5), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 6), "b"):
                        return True
            elif not kingside and rights["wQ"] and king_pos == (7, 4):
                if chessboard.board[7][1] == "--" and chessboard.board[7][2] == "--" and chessboard.board[7][3] == "--":
                    if not ChessRules.is_square_attacked(chessboard, (7, 4), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 3), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 2), "b"):
                        return True
        else:
            if kingside and rights["bK"] and king_pos == (0, 4):
                if chessboard.board[0][5] == "--" and chessboard.board[0][6] == "--":
                    if not ChessRules.is_square_attacked(chessboard, (0, 4), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 5), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 6), "w"):
                        return True
            elif not kingside and rights["bQ"] and king_pos == (0, 4):
                if chessboard.board[0][1] == "--" and chessboard.board[0][2] == "--" and chessboard.board[0][3] == "--":
                    if not ChessRules.is_square_attacked(chessboard, (0, 4), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 3), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 2), "w"):
                        return True
        return False

    @staticmethod
    def en_passant(chessboard, start, end):
        """
        Validación completa de en passant:
        - existe en_passant_square y coincide con end
        - la pieza en start es un peón
        - el movimiento start->end es una diagonal de 1 en la dirección correcta
        - en la casilla que sería capturada (fila start_row, columna end_col)
          debe haber un peón enemigo
        """
        sr, sc = start
        er, ec = end

        # límites
        if not (0 <= sr < 8 and 0 <= sc < 8 and 0 <= er < 8 and 0 <= ec < 8):
            return False

        piece = chessboard.board[sr][sc]
        if piece == "--" or piece[1] != "p":
            return False

        # debe existir y coincidir la casilla de en_passant
        if chessboard.en_passant_square is None:
            return False
        if (er, ec) != chessboard.en_passant_square:
            return False

        # dirección: las blancas se mueven "hacia arriba" en tu indexing (-1), negras hacia abajo (+1)
        direction = -1 if piece[0] == "w" else 1

        # el movimiento debe ser un diagonal de 1 en la dirección correcta
        if (er - sr) != direction or abs(ec - sc) != 1:
            return False

        # la casilla del peón vulnerable está en la fila sr y columna ec
        cap_r, cap_c = sr, ec
        if not (0 <= cap_r < 8 and 0 <= cap_c < 8):
            return False
        captured = chessboard.board[cap_r][cap_c]
        # debe haber un peón enemigo ahí
        if captured == "--" or captured[1] != "p" or captured[0] == piece[0]:
            return False

        return True

    @staticmethod
    def promote(chessboard, row, col, new_piece="q"):
        piece = chessboard.board[row][col]
        if piece == "wp" and row == 0:
            chessboard.board[row][col] = "w" + new_piece
        elif piece == "bp" and row == 7:
            chessboard.board[row][col] = "b" + new_piece

    @staticmethod
    def is_square_attacked(chessboard, square, enemy_color):
        """
        Devuelve True si la casilla está atacada por alguna pieza de enemy_color.
        """
        board = chessboard.board
        r, c = square

        # --- Peones ---
        if enemy_color == "w":  # peones blancos atacan hacia abajo (hacia mayor fila)
            attack_dirs = [(1, -1), (1, 1)]
        else:  # peones negros atacan hacia arriba (hacia menor fila)
            attack_dirs = [(-1, -1), (-1, 1)]

        for dr, dc in attack_dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if board[nr][nc] == enemy_color + "p":
                    return True

        # --- Caballos ---
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                        (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in knight_moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if board[nr][nc] == enemy_color + "n":
                    return True

        # --- Alfiles y Damas (diagonales) ---
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            nr, nc = r, c
            while True:
                nr += dr
                nc += dc
                if not (0 <= nr < 8 and 0 <= nc < 8):
                    break
                if board[nr][nc] != "--":
                    if board[nr][nc] in [enemy_color + "b", enemy_color + "q"]:
                        return True
                    break

        # --- Torres y Damas (líneas rectas) ---
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dr, dc in directions:
            nr, nc = r, c
            while True:
                nr += dr
                nc += dc
                if not (0 <= nr < 8 and 0 <= nc < 8):
                    break
                if board[nr][nc] != "--":
                    if board[nr][nc] in [enemy_color + "r", enemy_color + "q"]:
                        return True
                    break

        # --- Rey enemigo ---
        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in king_moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if board[nr][nc] == enemy_color + "k":
                    return True

        return False

    @staticmethod
    def is_in_check(chessboard, color):
        king_pos = chessboard.white_king_pos if color == "w" else chessboard.black_king_pos
        enemy_color = "b" if color == "w" else "w"
        return ChessRules.is_square_attacked(chessboard, king_pos, enemy_color)

    @staticmethod
    def is_special_move(chessboard, start, end):
        piece = chessboard.board[start[0]][start[1]]
        # Enroque solo si can_castle lo permite
        if piece[1] == "k":
            if piece[0] == "w":
                if end == (7, 6) and ChessRules.can_castle(chessboard, "w", kingside=True):
                    return True
                if end == (7, 2) and ChessRules.can_castle(chessboard, "w", kingside=False):
                    return True
            else:
                if end == (0, 6) and ChessRules.can_castle(chessboard, "b", kingside=True):
                    return True
                if end == (0, 2) and ChessRules.can_castle(chessboard, "b", kingside=False):
                    return True
        # En passant
        if piece[1] == "p" and ChessRules.en_passant(chessboard, start, end):
            return True
        return False

    @staticmethod
    def apply_special_move(chessboard, start, end):
        board = chessboard.board
        piece = board[start[0]][start[1]]

        # Enroque
        if piece[1] == "k":
            if piece[0] == "w":
                if end == (7, 6):  # enroque corto blanco
                    board[7][6] = "wk"
                    board[7][4] = "--"
                    board[7][5] = "wr"
                    board[7][7] = "--"
                    chessboard.white_king_pos = (7, 6)
                elif end == (7, 2):  # enroque largo blanco
                    board[7][2] = "wk"
                    board[7][4] = "--"
                    board[7][3] = "wr"
                    board[7][0] = "--"
                    chessboard.white_king_pos = (7, 2)
            else:
                if end == (0, 6):  # enroque corto negro
                    board[0][6] = "bk"
                    board[0][4] = "--"
                    board[0][5] = "br"
                    board[0][7] = "--"
                    chessboard.black_king_pos = (0, 6)
                elif end == (0, 2):  # enroque largo negro
                    board[0][2] = "bk"
                    board[0][4] = "--"
                    board[0][3] = "br"
                    board[0][0] = "--"
                    chessboard.black_king_pos = (0, 2)

        # En passant
        elif piece[1] == "p" and ChessRules.en_passant(chessboard, start, end):
            direction = -1 if piece[0] == "w" else 1
            board[end[0]][end[1]] = piece
            board[start[0]][start[1]] = "--"
            board[end[0] - direction][end[1]] = "--"  # eliminar peón capturado
            chessboard.en_passant_square = None

    @staticmethod
    def is_checkmate(board, color):
        # 1. ¿El rey de este color está en jaque?
        if not ChessRules.is_in_check(board, color):
            return False

        # 2. ¿Hay algún movimiento legal que lo salve?
        moves = board.get_legal_moves(color)
        for move in moves:
            board.make_move(move)
            if not ChessRules.is_in_check(board, color):
                board.undo_move()
                return False  # Encontró un movimiento que lo salva
            board.undo_move()

        # Si no hay escape:
        return True

    @staticmethod
    def is_stalemate(board, color):
        # 1. Si el rey está en jaque, no es ahogado
        if ChessRules.is_in_check(board, color):
            return False

        # 2. Si tiene al menos un movimiento legal, no es ahogado
        moves = board.get_legal_moves(color)
        for move in moves:
            board.make_move(move)
            if not ChessRules.is_in_check(board, color):
                board.undo_move()
                return False
            board.undo_move()

        # 3. Si no hay movimiento legal, es ahogado
        return True