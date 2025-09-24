# test_checkmate_stalemate.py
from chessLogic.chessboard import ChessBoard # Importa la clase ChessBoard.
from chessLogic.move import Move # Importa la clase Move.
from IA.move_generator import MoveGenerator # Importa MoveGenerator (aunque no se usa directamente en este test).
from IA.search import get_best_move # Importa get_best_move (aunque no se usa directamente en este test).
from chessLogic.rules import ChessRules # Importa ChessRules para verificar jaque mate y ahogado.

def play_sequence(board, moves_list):
    """
    Aplica una secuencia de jugadas en notación ((r1,c1),(r2,c2)) al tablero.
    
    Args:
        board (ChessBoard): La instancia del tablero de ajedrez.
        moves_list (list): Una lista de tuplas de movimientos ((start_row, start_col), (end_row, end_col)).
    """
    for start, end in moves_list: # Itera sobre cada movimiento en la lista.
        move = Move(start, end, board, promotion_choice="q") # Crea un objeto Move (asumiendo promoción a reina por defecto).
        if board.is_valid_move(start, end): # Verifica si el movimiento es válido.
            board.make_move(move) # Realiza el movimiento si es válido.
        else:
            print(f"❌ Movimiento {start}->{end} no válido") # Imprime un error si el movimiento no es válido.
            break # Detiene la secuencia si un movimiento es inválido.

def test_checkmate_detection():
    """
    Prueba la detección de jaque mate con un ejemplo conocido (Fool's Mate).
    """
    board = ChessBoard() # Crea un nuevo tablero de ajedrez.

    # Ejemplo de jaque mate: Fool's Mate (blancas pierden).
    # Esta secuencia de movimientos lleva a un jaque mate rápido para las blancas.
    sequence = [
        ((6, 5), (5, 5)),  # f3 (Peón blanco de f2 a f3)
        ((1, 4), (3, 4)),  # e5 (Peón negro de e7 a e5)
        ((6, 6), (4, 6)),  # g4 (Peón blanco de g2 a g4)
        ((0, 3), (4, 7))   # Qh4# (Reina negra de d8 a h4, jaque mate)
    ]

    play_sequence(board, sequence) # Aplica la secuencia de movimientos al tablero.

    print("\n=== Estado después de Fool's Mate ===")
    print("Turno:", board.turn) # Imprime el turno actual.
    print("Rey en jaque:", ChessRules.is_in_check(board, board.turn)) # Verifica si el rey del turno actual está en jaque.
    
    # Verifica si se detecta jaque mate o ahogado.
    if ChessRules.is_checkmate(board, board.turn):
        print("❌ Jaque mate detectado correctamente") # Si es jaque mate, imprime éxito.
    elif ChessRules.is_stalemate(board, board.turn):
        print("♟ Ahogado detectado") # Si es ahogado, imprime.
    else:
        print("✅ Juego sigue") # Si no es ninguno, imprime que el juego sigue.

if __name__ == "__main__":
    test_checkmate_detection() # Ejecuta la función de prueba si el script se ejecuta directamente.


