# chessLogic/rules.py
from .utils import get_all_moves

class ChessRules:

    @staticmethod
    def can_castle(chessboard, color, kingside=True):
        rights = chessboard.castling_rights
        king_pos = chessboard.white_king_pos if color == "w" else chessboard.black_king_pos
        row, col = king_pos

        if color == "w":
            if kingside and rights["wK"]:
                if chessboard.board[7][5] == "--" and chessboard.board[7][6] == "--":
                    if not ChessRules.is_square_attacked(chessboard, (7, 4), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 5), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 6), "b"):
                        return True
            elif not kingside and rights["wQ"]:
                if chessboard.board[7][1] == "--" and chessboard.board[7][2] == "--" and chessboard.board[7][3] == "--":
                    if not ChessRules.is_square_attacked(chessboard, (7, 4), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 3), "b") and \
                       not ChessRules.is_square_attacked(chessboard, (7, 2), "b"):
                        return True
        else:
            if kingside and rights["bK"]:
                if chessboard.board[0][5] == "--" and chessboard.board[0][6] == "--":
                    if not ChessRules.is_square_attacked(chessboard, (0, 4), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 5), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 6), "w"):
                        return True
            elif not kingside and rights["bQ"]:
                if chessboard.board[0][1] == "--" and chessboard.board[0][2] == "--" and chessboard.board[0][3] == "--":
                    if not ChessRules.is_square_attacked(chessboard, (0, 4), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 3), "w") and \
                       not ChessRules.is_square_attacked(chessboard, (0, 2), "w"):
                        return True
        return False

    @staticmethod
    def en_passant(chessboard, start, end):
        return chessboard.en_passant_possible == end

    @staticmethod
    def promote(chessboard, row, col, new_piece="q"):
        piece = chessboard.board[row][col]
        if piece == "wp" and row == 0:
            chessboard.board[row][col] = "w" + new_piece
        elif piece == "bp" and row == 7:
            chessboard.board[row][col] = "b" + new_piece

    @staticmethod
    def is_square_attacked(chessboard, square, by_color):
        enemy_moves = get_all_moves(chessboard, by_color, pseudo_legal=True)
        return square in [m[1] for m in enemy_moves]

    @staticmethod
    def is_in_check(chessboard, color):
        king_pos = chessboard.white_king_pos if color == "w" else chessboard.black_king_pos
        enemy_color = "b" if color == "w" else "w"
        return ChessRules.is_square_attacked(chessboard, king_pos, enemy_color)

    @staticmethod
    def is_special_move(chessboard, start, end):
        piece = chessboard.board[start[0]][start[1]]
        return (piece[1] == "k" and abs(end[1]-start[1])==2) or \
               (piece[1]=="p" and ChessRules.en_passant(chessboard, start, end))

    @staticmethod
    def apply_special_move(chessboard, start, end):
        board = chessboard.board
        piece = board[start[0]][start[1]]

        # Enroque
        if piece[1] == "k" and abs(end[1] - start[1]) == 2:
            row = start[0]
            if end[1] > start[1]:  # enroque corto
                board[row][6] = piece
                board[row][4] = "--"
                rook = board[row][7]
                board[row][5] = rook
                board[row][7] = "--"
            else:  # enroque largo
                board[row][2] = piece
                board[row][4] = "--"
                rook = board[row][0]
                board[row][3] = rook
                board[row][0] = "--"
            # Actualizar posición del rey
            if piece[0] == "w":
                chessboard.white_king_pos = (row, end[1])
            else:
                chessboard.black_king_pos = (row, end[1])

        # En passant
        elif piece[1] == "p" and ChessRules.en_passant(chessboard, start, end):
            direction = -1 if piece[0] == "w" else 1
            board[end[0]][end[1]] = piece
            board[start[0]][start[1]] = "--"
            board[end[0] - direction][end[1]] = "--"  # eliminar peón capturado
            chessboard.en_passant_possible = None
