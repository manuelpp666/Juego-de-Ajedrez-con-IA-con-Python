# test_checkmate_stalemate.py
from chessLogic.chessboard import ChessBoard
from chessLogic.move import Move
from IA.move_generator import MoveGenerator
from IA.search import get_best_move
from chessLogic.rules import ChessRules

def play_sequence(board, moves_list):
    """Aplica una secuencia de jugadas en notación ((r1,c1),(r2,c2))"""
    for start, end in moves_list:
        move = Move(start, end, board, promotion_choice="q")
        if board.is_valid_move(start, end):
            board.make_move(move)
        else:
            print(f"❌ Movimiento {start}->{end} no válido")
            break

def test_checkmate_detection():
    board = ChessBoard()

    # Ejemplo de jaque mate: Fool's Mate (blancas pierden)
    sequence = [
        ((6, 5), (5, 5)),  # f3
        ((1, 4), (3, 4)),  # e5
        ((6, 6), (4, 6)),  # g4
        ((0, 3), (4, 7))   # Qh4#
    ]

    play_sequence(board, sequence)

    print("\n=== Estado después de Fool's Mate ===")
    print("Turno:", board.turn)
    print("Rey en jaque:", ChessRules.is_in_check(board, board.turn))
    if ChessRules.is_checkmate(board, board.turn):
        print("❌ Jaque mate detectado correctamente")
    elif ChessRules.is_stalemate(board, board.turn):
        print("♟ Ahogado detectado")
    else:
        print("✅ Juego sigue")

if __name__ == "__main__":
    test_checkmate_detection()
