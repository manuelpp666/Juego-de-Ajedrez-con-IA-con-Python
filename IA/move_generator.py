# IA/move_generator.py
from chessLogic.moves import is_legal_move
from chessLogic.rules import ChessRules
from chessLogic.move import Move

class MoveGenerator:

    @staticmethod
    def generate_pseudo_legal_moves(chessboard, color):
        """
        Genera todos los movimientos pseudo-legales de manera más eficiente.
        - Revisa movimientos geométricos de la pieza.
        - NO comprueba si dejan al rey en jaque.
        """
        moves = []
        board = chessboard.board

        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece != "--" and piece[0] == color:
                    p_type = piece[1]
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
                        # Añadir enroque como pseudo-legal aquí para que minimax lo evalúe
                        if ChessRules.can_castle(chessboard, color, kingside=True):
                            moves.append(((r, c), (r, c + 2)))
                        if ChessRules.can_castle(chessboard, color, kingside=False):
                            moves.append(((r, c), (r, c - 2)))
        return moves

    @staticmethod
    def _get_pawn_moves(chessboard, start_pos, color):
        moves = []
        sr, sc = start_pos
        direction = -1 if color == "w" else 1
        
        # Movimiento de un paso
        er, ec = sr + direction, sc
        if 0 <= er < 8 and chessboard.board[er][ec] == "--":
            moves.append((start_pos, (er, ec)))
            # Movimiento de dos pasos
            if (sr == 6 and color == "w") or (sr == 1 and color == "b"):
                er2 = sr + 2 * direction
                if chessboard.board[er2][ec] == "--" and chessboard.board[sr + direction][sc] == "--":
                    moves.append((start_pos, (er2, ec)))
        
        # Capturas
        for dc in [-1, 1]:
            er, ec = sr + direction, sc + dc
            if 0 <= er < 8 and 0 <= ec < 8:
                target_piece = chessboard.board[er][ec]
                if target_piece != "--" and target_piece[0] != color:
                    moves.append((start_pos, (er, ec)))
                # En passant
                if chessboard.en_passant_square == (er, ec):
                    moves.append((start_pos, (er, ec)))
        return moves

    @staticmethod
    def _get_rook_moves(chessboard, start_pos, color):
        moves = []
        sr, sc = start_pos
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            for i in range(1, 8):
                er, ec = sr + dr * i, sc + dc * i
                if not (0 <= er < 8 and 0 <= ec < 8):
                    break
                target_piece = chessboard.board[er][ec]
                if target_piece == "--":
                    moves.append((start_pos, (er, ec)))
                elif target_piece[0] != color:
                    moves.append((start_pos, (er, ec)))
                    break
                else: # Pieza del mismo color
                    break
        return moves

    @staticmethod
    def _get_knight_moves(chessboard, start_pos, color):
        moves = []
        sr, sc = start_pos
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                        (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in knight_moves:
            er, ec = sr + dr, sc + dc
            if 0 <= er < 8 and 0 <= ec < 8:
                target_piece = chessboard.board[er][ec]
                if target_piece == "--" or target_piece[0] != color:
                    moves.append((start_pos, (er, ec)))
        return moves

    @staticmethod
    def _get_bishop_moves(chessboard, start_pos, color):
        moves = []
        sr, sc = start_pos
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                er, ec = sr + dr * i, sc + dc * i
                if not (0 <= er < 8 and 0 <= ec < 8):
                    break
                target_piece = chessboard.board[er][ec]
                if target_piece == "--":
                    moves.append((start_pos, (er, ec)))
                elif target_piece[0] != color:
                    moves.append((start_pos, (er, ec)))
                    break
                else: # Pieza del mismo color
                    break
        return moves

    @staticmethod
    def _get_queen_moves(chessboard, start_pos, color):
        # La reina combina movimientos de torre y alfil
        return MoveGenerator._get_rook_moves(chessboard, start_pos, color) + \
               MoveGenerator._get_bishop_moves(chessboard, start_pos, color)

    @staticmethod
    def _get_king_moves(chessboard, start_pos, color):
        moves = []
        sr, sc = start_pos
        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in king_moves:
            er, ec = sr + dr, sc + dc
            if 0 <= er < 8 and 0 <= ec < 8:
                target_piece = chessboard.board[er][ec]
                if target_piece == "--" or target_piece[0] != color:
                    moves.append((start_pos, (er, ec)))
        return moves

    @staticmethod
    def generate_legal_moves(chessboard, color):
        """
        Genera movimientos legales reales.
        - Parte de los pseudo-legales.
        - Hace y deshace cada movimiento en el tablero temporalmente.
        - Elimina los movimientos que dejan al propio rey en jaque.
        """
        legal_moves = []
        pseudo_moves = MoveGenerator.generate_pseudo_legal_moves(chessboard, color)

        for start, end in pseudo_moves:
            # Crear un objeto Move para el movimiento actual
            move = Move(start, end, chessboard)
            
            # Simular el movimiento
            chessboard.make_move(move)

            # Verificar si el rey del color actual está en jaque después del movimiento
            if not ChessRules.is_in_check(chessboard, color):
                legal_moves.append((start, end))

            # Revertir el movimiento para restaurar el estado del tablero
            chessboard.undo_move()

        return legal_moves

    @staticmethod
    def has_any_legal_moves(chessboard, color):
        """
        Comprueba si un jugador tiene al menos un movimiento legal.
        Útil para detectar jaque mate o tablas por ahogado.
        """
        # Optimización: solo necesitamos encontrar UN movimiento legal
        pseudo_moves = MoveGenerator.generate_pseudo_legal_moves(chessboard, color)

        for start, end in pseudo_moves:
            move = Move(start, end, chessboard)
            chessboard.make_move(move)
            if not ChessRules.is_in_check(chessboard, color):
                chessboard.undo_move() # Revertir antes de retornar
                return True
            chessboard.undo_move()
        return False
