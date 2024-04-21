import chess

def find_candidate_moves(board):
    candidate_moves = []
    legal_moves = list(board.legal_moves)

    # Проверка на шах и мат
    if board.is_checkmate():
        return legal_moves  # Если мат, то все доступные ходы приводят к мату
    if board.is_check():
        # Если шах, добавляем все ходы, которые блокируют шах или уводят короля
        for move in legal_moves:
            board.push(move)
            if not board.is_check():
                candidate_moves.append(move)
            board.pop()
        return candidate_moves
    
    # Взятие фигур
    for move in legal_moves:
        if board.is_capture(move):
            candidate_moves.append(move)
    
    return candidate_moves
