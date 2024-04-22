import chess 


def evaluate_ideal_pieces(board):
    
    CENTER_FILES = chess.BB_FILE_C | chess.BB_FILE_D | chess.BB_FILE_E | chess.BB_FILE_F
    CENTER_RANKS = chess.BB_RANK_3 | chess.BB_RANK_4 | chess.BB_RANK_5 | chess.BB_RANK_6
    CENTER_SQUARES = CENTER_FILES & CENTER_RANKS
    
    piece_scores = {'Белые': {}, 'Чёрные': {}}
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3.5,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }
    
    # Анализ каждой фигуры на доске
    for color in [chess.WHITE, chess.BLACK]:
        color_name = 'Белые' if color == chess.WHITE else 'Чёрные'
        for piece_type in piece_values.keys():
            pieces = board.pieces(piece_type, color)
            for square in pieces:
                score = 0
                
                # Мобильность: количество доступных ходов
                moves = list(board.attacks(square))
                score += len(moves)

                # Нападение на более ценные фигуры
                for move in moves:
                    attacked_piece = board.piece_at(move)
                    if attacked_piece and attacked_piece.color != color:
                        score += piece_values.get(attacked_piece.piece_type, 0)

                # Защита своими фигурами
                defended_by_own = len([move for move in board.attacks(square) if board.piece_at(move) and board.piece_at(move).color == color])
                score += defended_by_own

                # Позиционные бонусы за нахождение в центре
                if chess.square_rank(square) & CENTER_SQUARES:
                    score += 2  # Бонус за центральное положение

                piece_scores[color_name][chess.square_name(square)] = score

    # Определение идеальных фигур
    ideal_pieces = {'Белые': [], 'Чёрные': []}
    for color, scores in piece_scores.items():
        max_score = max(scores.values(), default=0)
        ideal_pieces[color] = [square for square, score in scores.items() if score == max_score]

    return ideal_pieces