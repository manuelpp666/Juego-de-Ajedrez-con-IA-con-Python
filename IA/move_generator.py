# IA/move_generator.py
from chessLogic.moves import is_legal_move
from chessLogic.rules import ChessRules
from chessLogic.move import Move

class MoveGenerator:

    @staticmethod
    def generate_pseudo_legal_moves(chessboard, color):
        """
        Genera todos los movimientos pseudo-legales.
        - Revisa movimientos geométricos de la pieza.
        - NO comprueba si dejan al rey en jaque.
        """
        moves = []
        board = chessboard.board

        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece != "--" and piece[0] == color:
                    for er in range(8):
                        for ec in range(8):
                            if is_legal_move(
                                chessboard,
                                (r, c),
                                (er, ec),
                                pseudo_legal=True  # <-- solo valida geometría
                            ):
                                moves.append(((r, c), (er, ec)))
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
            move = Move(start, end, chessboard)
            chessboard.make_move(move)

            # Determinar color contrario (necesario para verificar jaque)
            opponent_color = "b" if color == "w" else "w"

            # ✅ Solo se añade si el propio rey NO queda en jaque
            if not ChessRules.is_in_check(chessboard, color):
                legal_moves.append((start, end))

            # 🔄 revertir siempre después de probar
            chessboard.undo_move()

        return legal_moves

    @staticmethod
    def has_any_legal_moves(chessboard, color):
        """
        Comprueba si un jugador tiene al menos un movimiento legal.
        Útil para detectar jaque mate o tablas por ahogado.
        """
        moves = MoveGenerator.generate_legal_moves(chessboard, color)
        return len(moves) > 0
