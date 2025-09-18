# chessLogic/utils.py

def get_all_moves(chessboard, color, pseudo_legal=False):
    from .moves import is_legal_move
    

    moves_list = []
    board = chessboard.board

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != "--" and piece[0] == color:
                for er in range(8):
                    for ec in range(8):
                        if pseudo_legal:
                            # Movimientos pseudo-legales: solo reglas geométricas
                            if is_legal_move(chessboard, (r, c), (er, ec), pseudo_legal=True):
                                moves_list.append(((r, c), (er, ec)))
                        else:
                            # Movimientos legales completos
                            if is_legal_move(chessboard, (r, c), (er, ec), pseudo_legal=False):
                                moves_list.append(((r, c), (er, ec)))
    return moves_list
