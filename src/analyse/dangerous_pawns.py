import chess

def evaluate_dangerous_pawns(board):
    dangerous_pawns = {'Белые': [], 'Чёрные': []}
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3.5,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }

    # Проверка проходных пешек
    def is_passed_pawn(square, color):
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        enemy_color = chess.BLACK if color == chess.WHITE else chess.WHITE

        start_rank = rank + 1 if color == chess.WHITE else rank - 1
        end_rank = 7 if color == chess.WHITE else 0
        step = 1 if color == chess.WHITE else -1

        for rank in range(start_rank, end_rank + step, step):
            for offset in [-1, 0, 1]:
                test_square = chess.square(file + offset, rank)
                if 0 <= file + offset < 8 and board.piece_at(test_square) and board.color_at(test_square) == enemy_color:
                    return False
        return True

    # Анализ каждой пешки на доске
    for color in [chess.WHITE, chess.BLACK]:
        color_name = 'Белые' if color == chess.WHITE else 'Чёрные'
        for square in board.pieces(chess.PAWN, color):
            score = 0

            # Проверка, является ли пешка проходной
            if is_passed_pawn(square, color):
                score += 3

            # Проверка продвинутости пешки
            rank = chess.square_rank(square)
            score += (rank if color == chess.WHITE else 7 - rank) * 0.5

            # Защита пешки другими пешками или фигурами
            defenders = len(board.attackers(color, square))
            score += defenders

            # Нападение на фигуры противника
            attacks = len([move for move in board.attacks(square) if board.piece_at(move) and board.color_at(move) != color])
            score += attacks * 0.5

            # Добавление пешки в список, если она достаточно "опасна"
            if score > 3:  # Примерный порог опасности
                dangerous_pawns[color_name].append(chess.square_name(square))

    return dangerous_pawns
