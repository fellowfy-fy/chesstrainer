import chess
import pandas as pd

def get_piece_name(piece, square, figure_mapping):
    """ Возвращает альтернативное название фигуры или стандартное, основываясь на позиции. """
    if piece is None:
        return ''
    # Словарь стандартных названий фигур
    standard_names = {
        chess.PAWN: 'Пешка',
        chess.KNIGHT: 'Конь',
        chess.BISHOP: 'Слон',
        chess.ROOK: 'Ладья',
        chess.QUEEN: 'Ферзь',
        chess.KING: 'Король'
    }
    standard_name = standard_names.get(piece.piece_type, 'Неизвестно')
    square_name = square
    # Проверяем, содержится ли текущая позиция в значении словаря figure_mapping
    for name, pos in figure_mapping.items():
        if pos == square_name:
            return name  # Возвращаем альтернативное название, если нашли совпадение
    return standard_name  # Возвращаем стандартное название, если не нашли совпадений

def generate_moves_table(board, figure_mapping):

    moves_white = []
    moves_black = []

    # Сохраняем текущую позицию для возврата после генерации ходов
    snapshot = board.fen()

    # Генерация ходов для белых
    board.turn = chess.WHITE
    for move in board.legal_moves:
        board.push(move)
        piece = board.piece_at(move.to_square)
        piece_name = get_piece_name(piece, chess.square_name(move.from_square), figure_mapping)
        moves_white.append(f"{piece_name} {chess.square_name(move.from_square)} -> {chess.square_name(move.to_square)}")
        board.pop()

    # Генерация ходов для черных
    board.turn = chess.BLACK
    for move in board.legal_moves:
        board.push(move)
        piece = board.piece_at(move.to_square)
        piece_name = get_piece_name(piece, chess.square_name(move.from_square), figure_mapping)
        moves_black.append(f"{piece_name} {chess.square_name(move.from_square)} -> {chess.square_name(move.to_square)}")
        board.pop()

    # Возвращаем доску в исходное состояние
    board.set_fen(snapshot)

    # Создание DataFrame
    max_len = max(len(moves_white), len(moves_black))
    if len(moves_white) < max_len:
        moves_white.extend([""] * (max_len - len(moves_white)))
    if len(moves_black) < max_len:
        moves_black.extend([""] * (max_len - len(moves_black)))

    df = pd.DataFrame({
        'Белые': moves_white,
        'Чёрные': moves_black
    })

    return df