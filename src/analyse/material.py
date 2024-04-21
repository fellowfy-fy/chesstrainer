import chess
def evaluate_material(board):
    # Определение веса фигур в пешках
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3.5,
        chess.ROOK: 5,
        chess.QUEEN: 9
        # Король не оценивается в пешках, так как он бесценен
    }

    # Подсчет материала для каждого цвета
    white_material = 0
    black_material = 0

    for piece_type in piece_values:
        white_pieces = board.pieces(piece_type, chess.WHITE)
        black_pieces = board.pieces(piece_type, chess.BLACK)

        white_material += sum(piece_values[piece_type] for _ in white_pieces)
        black_material += sum(piece_values[piece_type] for _ in black_pieces)

    return white_material, black_material