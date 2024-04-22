import chess
import random

def find_candidate_moves(board):
    candidate_moves = []
    legal_moves = list(board.legal_moves)

    # Проверка на шах и мат
    if board.is_checkmate():
        # Если мат, то все доступные ходы приводят к мату
        return legal_moves
    if board.is_check():
        # Если шах, добавляем все ходы, которые блокируют шах или уводят короля
        for move in legal_moves:
            board.push(move)
            if not board.is_check():
                candidate_moves.append(move)
            board.pop()
        if candidate_moves:
            return candidate_moves
    
    # Взятие фигур
    for move in legal_moves:
        if board.is_capture(move):
            candidate_moves.append(move)

    # Если не найдены специфические ходы-кандидаты, возвращаем первый допустимый ход
    if not candidate_moves:
        candidate_moves.append(random.choice(legal_moves)) if legal_moves else None

    return candidate_moves
