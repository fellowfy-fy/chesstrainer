import chess

def analyze_flank_activity(board):
    # Создание масок для каждого фланга
    queen_flank = chess.BB_FILES[0] | chess.BB_FILES[1] | chess.BB_FILES[2] | chess.BB_FILES[3]  # Файлы a-d
    center = chess.BB_FILES[4] | chess.BB_FILES[5]  # Файлы e-f
    king_flank = chess.BB_FILES[6] | chess.BB_FILES[7]  # Файлы g-h

    # Словарь для сбора результатов
    activity = {
        'ферзевый фланг': {'white': 0, 'black': 0},
        'центр': {'white': 0, 'black': 0},
        'королевский фланг': {'white': 0, 'black': 0}
    }

    # Анализ каждого фланга
    flanks = {
        'ферзевый фланг': queen_flank,
        'центр': center,
        'королевский фланг': king_flank
    }

    for flank, squares in flanks.items():
        for square in chess.scan_reversed(squares):
            if board.is_attacked_by(chess.WHITE, square):
                activity[flank]['white'] += 1
            if board.is_attacked_by(chess.BLACK, square):
                activity[flank]['black'] += 1

    # Вычисление баланса на каждом фланге
    for flank in activity:
        if activity[flank]['white'] == activity[flank]['black']:
            activity[flank] = 'Баланс'
        elif activity[flank]['white'] > activity[flank]['black']:
            activity[flank] = 'Белые'
        else:
            activity[flank] = 'Черные'

    return activity
