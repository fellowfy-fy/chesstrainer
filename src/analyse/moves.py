import chess
import pandas as pd

def generate_moves_table(board):
    piece_names = {
        'P': 'Пешка',
        'N': 'Конь',
        'B': 'Слон',
        'R': 'Ладья',
        'Q': 'Ферзь',
        'K': 'Король'
    }

    moves_white = []
    moves_black = []

    # Сохраняем текущую позицию для возврата после генерации ходов
    snapshot = board.fen()

    # Генерация ходов для белых
    board.turn = chess.WHITE
    for move in board.legal_moves:
        board.push(move)
        piece = board.piece_at(move.to_square)
        piece_name = piece_names[piece.symbol().upper()] if piece else "None"
        moves_white.append(f"{piece_name} {chess.square_name(move.from_square)} -> {chess.square_name(move.to_square)}")
        board.pop()

    # Генерация ходов для черных
    board.turn = chess.BLACK
    for move in board.legal_moves:
        board.push(move)
        piece = board.piece_at(move.to_square)
        piece_name = piece_names[piece.symbol().upper()] if piece else "None"
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