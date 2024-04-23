import chess
def determine_game_stage(board):
    # Подсчет фигур для определения стадии
    total_material = sum(
        1 for piece in board.piece_map().values() if piece.piece_type != chess.KING
    )
    if total_material >= 30:
        return "Дебют"
    elif 16 < total_material < 30:
        return "Стратегическая"
    else:
        return "Окончание"
