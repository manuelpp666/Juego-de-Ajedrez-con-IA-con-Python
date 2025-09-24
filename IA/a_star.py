# IA/a_star.py
import heapq # Importa heapq para implementar una cola de prioridad (min-heap).
import itertools # Importa itertools para generar contadores únicos.
from IA.evaluation import evaluate_board # Importa la función de evaluación del tablero.
from IA.move_generator import MoveGenerator # Importa la clase MoveGenerator para obtener movimientos.
from chessLogic.move import Move # Importa la clase Move para representar los movimientos.


def get_best_move_astar(board, depth_limit=2, beam_width=5):
    """
    Algoritmo A* adaptado para ajedrez (modo fácil).
    Usa evaluación estática como heurística, con límite de profundidad y beam search.
    Se apoya en make_move / undo_move en vez de copiar tableros completos para eficiencia.
    
    Args:
        board (ChessBoard): La instancia actual del tablero de ajedrez.
        depth_limit (int, optional): La profundidad máxima de búsqueda. Por defecto es 2.
        beam_width (int, optional): El ancho del haz para el beam search (número de mejores nodos a expandir).
                                    Por defecto es 5.
                                    
    Returns:
        Move: El mejor movimiento encontrado por el algoritmo A*.
    """

    counter = itertools.count()  # Contador único para cada entrada en la cola de prioridad (para desempates).

    # Nodo inicial en la cola: (f, g, h, depth, move_sequence)
    # f = g + h (costo total estimado)
    # g = costo real desde el inicio (profundidad)
    # h = costo heurístico estimado hasta el objetivo (evaluación del tablero)
    start_eval = evaluate_board(board) # Evaluación del tablero inicial.
    start_node = (start_eval, 0, start_eval, 0, []) # (f, g, h, profundidad, secuencia de movimientos).

    # La frontera es una cola de prioridad (min-heap).
    # Almacena (-f, id_unico, nodo) para que heapq funcione como max-heap (prioridad por mayor f).
    frontier = [(-start_node[0], next(counter), start_node)]
    best_move = None # Variable para almacenar el mejor movimiento encontrado.

    while frontier: # Mientras haya nodos en la frontera.
        # Extrae el nodo con la mayor prioridad (mayor f) de la cola.
        _, _, (f, g, h, depth, move_seq) = heapq.heappop(frontier)

        # Si alcanzamos la profundidad límite, consideramos el primer movimiento de esta secuencia
        # como un candidato para el mejor movimiento y continuamos con otros nodos.
        if depth >= depth_limit:
            if move_seq:
                # Si es el primer movimiento en la secuencia, lo consideramos el mejor hasta ahora.
                # Esto es una simplificación para A* en ajedrez, donde el "objetivo" es encontrar
                # el mejor movimiento inicial, no una secuencia completa.
                if best_move is None or f > evaluate_board(board): # Comparación simplificada.
                    best_move = move_seq[0]
            continue # No expandimos más allá del límite de profundidad.

        # Generar movimientos legales desde el tablero actual para el jugador actual.
        legal_moves = MoveGenerator.generate_legal_moves(board, board.turn)

        # Asegurar que todos los movimientos sean instancias de la clase Move.
        fixed_moves = []
        for m in legal_moves:
            if isinstance(m, Move):
                fixed_moves.append(m)
            else:
                try:
                    # Si el movimiento es una tupla (start, end), lo convierte a un objeto Move.
                    start_sq, end_sq = m
                    fixed_moves.append(Move(start_sq, end_sq, board))
                except Exception:
                    continue # Ignora movimientos mal formados.

        scored_moves = [] # Lista para almacenar los movimientos con sus evaluaciones.
        for move in fixed_moves:
            board.make_move(move) # Realiza el movimiento en el tablero (simulación).
            eval_score = evaluate_board(board) # Evalúa el tablero después del movimiento.
            board.undo_move() # Deshace el movimiento para restaurar el tablero.

            # Calcula la heurística 'h_new'. Si es el turno de las negras, se invierte la evaluación.
            if board.turn == "b":
                h_new = -eval_score
            else:
                h_new = eval_score

            g_new = g + 1 # El costo real (profundidad) aumenta en 1.
            f_new = g_new + h_new # Calcula el nuevo costo total estimado.
            scored_moves.append((f_new, g_new, h_new, move)) # Añade el movimiento con sus puntuaciones.

        # Beam search: selecciona solo los 'beam_width' mejores movimientos para expandir.
        scored_moves.sort(key=lambda x: x[0], reverse=True) # Ordena por f_new de mayor a menor.
        scored_moves = scored_moves[:beam_width] # Toma solo los mejores.

        for f_new, g_new, h_new, move in scored_moves:
            board.make_move(move) # Realiza el movimiento para el siguiente nivel de búsqueda.
            heapq.heappush(
                frontier,
                # Añade el nuevo nodo a la frontera.
                # La secuencia de movimientos se actualiza con el movimiento actual.
                (-f_new, next(counter), (f_new, g_new, h_new, depth + 1, move_seq + [move]))
            )
            board.undo_move() # Deshace el movimiento para restaurar el tablero.

    return best_move # Devuelve el mejor movimiento encontrado.


