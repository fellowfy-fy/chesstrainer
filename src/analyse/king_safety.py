import chess

def evaluate_king_safety(board, color):
    king_square = board.king(color)
    if king_square is None:
        return None  # Король может быть снят с доски в некоторых позициях, таких как тесты

    # Позиции вокруг короля, куда он может совершить ход, включая текущую позицию
    king_zone = board.attacks(king_square) | {king_square}
    
    # 1. Пешечное прикрытие в процентах
    own_pawns = board.pieces(chess.PAWN, color)
    pawn_cover = len(king_zone & own_pawns) / len(king_zone) * 100
    
    # 2. Угрозы в шах и мат
    in_check = board.is_check()
    checkmate = board.is_checkmate()
    
    # 3. Наличие ферзей
    queens_present = bool(board.pieces(chess.QUEEN, color))
    
    # 4. Близость к своей линии в процентах
    king_rank = chess.square_rank(king_square)
    rank_distance = abs(king_rank - (0 if color == chess.WHITE else 7)) / 7 * 100
    
    # 5. Свобода в процентах
    legal_moves = len(list(board.legal_moves))
    king_moves = len([move for move in board.legal_moves if move.from_square == king_square])
    freedom_percentage = (king_moves / legal_moves * 100) if legal_moves else 0
    
    # 6. Атака противника
    opponent_attacks = any(board.is_attacked_by(not color, sq) for sq in king_zone)
    
    return {
        "pawn_cover_percent": pawn_cover,
        "in_check": in_check,
        "checkmate": checkmate,
        "queens_present": queens_present,
        "rank_distance_percent": rank_distance,
        "freedom_percent": freedom_percentage,
        "opponent_attacking": opponent_attacks
    }

def evaluate_king_safety_for_both_sides(board):
    # Оценка безопасности для обоих королей
    white_safety = evaluate_king_safety(board, chess.WHITE)
    black_safety = evaluate_king_safety(board, chess.BLACK)
    
    # Объединение результатов в один словарь
    safety_metrics = {'white': white_safety, 'black': black_safety}
    return safety_metrics