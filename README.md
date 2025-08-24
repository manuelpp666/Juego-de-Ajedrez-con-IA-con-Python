chess-ai/
│── gui/              # Interfaz gráfica (tablero, piezas, interacción usuario)
│   ├── __init__.py
│   ├── board.py      # Lógica para dibujar el tablero
│   ├── pieces.py     # Manejo de imágenes y piezas
│   └── gui.py        # Ventana principal (controlador gráfico)
│
│── engine/           # Aquí irá después tu motor (IA, minimax, etc.)
│   ├── __init__.py
│   ├── move_generator.py
│   ├── evaluation.py
│   └── search.py
│
│── chessLogic/             # Lógica del ajedrez en sí (independiente del GUI)
│   ├── __init__.py
│   ├── chessboard.py # Representación del tablero en memoria (8x8, FEN, etc.)
│   ├── moves.py      # Reglas de movimiento de cada pieza
│   └── utils.py      # Funciones auxiliares
│
│── assets/           # Imágenes de las piezas (blancas y negras)
│   ├── wp.png        # Peón blanco
│   ├── bp.png        # Peón negro
│   ├── ...
│
│── main.py           # Punto de entrada: inicia el juego
