import chess


# Пешка считается проходной, если на ее пути к превращению нет других пешек на ее файле и на соседних файлах вплоть до конца доски.
# Пешка является изолированной, если рядом с ней нет пешек на соседних файлах.
# Пешка считается защитником короля, если она находится в одном ряду с королем или на соседнем ряду.
# Центральной пешкой является пешка на D или E файле.
# Пешка является сдвоенной, если в ее файле есть другая пешка того же цвета.
# Продвинутой пешкой считается пешка, которая достигла 6-го ряда или выше для белых и 3-го ряда или ниже для черных.



def analyze_pawns(board):
    results = {
        'Белые': {'Проходная': [], 'Изолированная': [], 'Защитники короля': [], 'Центральная': [], 'Сдвоенность': [], 'Продвинутая': []},
        'Чёрные': {'Проходная': [], 'Изолированная': [], 'Защитники короля': [], 'Центральная': [], 'Сдвоенность': [], 'Продвинутая': []}
    }
    for color in [chess.WHITE, chess.BLACK]:
        color_str = 'Белые' if color == chess.WHITE else 'Чёрные'
        for square in board.pieces(chess.PAWN, color):
            file = chess.square_file(square)
            rank = chess.square_rank(square)

            # Check for Проходная pawns
            is_passed = True
            for forward_rank in range(rank + 1, 8) if color == chess.WHITE else range(rank - 1, -1, -1):
                if any(board.piece_at(chess.square(f, forward_rank)) for f in [file-1, file, file+1] if 0 <= f < 8):
                    is_passed = False
                    break
            if is_passed:
                results[color_str]['Проходная'].append(chess.square_name(square))

            # Check for Изолированная pawns возможно неправильно считает
            is_isolated = not any(board.piece_at(chess.square(f, rank)) for f in [file - 1, file + 1] if 0 <= f < 8)
            if is_isolated:
                results[color_str]['Изолированная'].append(chess.square_name(square))

            # Check for king defenders
            king_square = board.king(color)
            if king_square and abs(chess.square_rank(king_square) - rank) <= 1:
                results[color_str]['Защитники короля'].append(chess.square_name(square))

            # Check for Центральная pawns
            if file in [3, 4]:  # Files D and E
                results[color_str]['Центральная'].append(chess.square_name(square))

            # Check for Сдвоенность pawns
            is_doubled = False
            for r in range(8):  # Просмотр всех рядов на файле
                if r != rank and board.piece_at(chess.square(file, r)) == chess.Piece(chess.PAWN, color):
                    is_doubled = True
                    break
            if is_doubled:
                results[color_str]['Сдвоенность'].append(chess.square_name(square))

            # Check for Продвинутая pawns
            if (color == chess.WHITE and rank >= 5) or (color == chess.BLACK and rank <= 2):
                results[color_str]['Продвинутая'].append(chess.square_name(square))

    return results
