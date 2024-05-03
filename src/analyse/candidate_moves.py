import chess
import random

def find_candidate_moves(board, color):
    candidate_moves = []
    original_turn = board.turn  # Сохраняем текущий ход для восстановления после операций

    # Установка текущего хода в соответствии с заданным цветом
    board.turn = color
    legal_moves = list(board.legal_moves)

    # Проверка на шах и мат
    if board.is_checkmate():
        # Если мат, то все доступные ходы приводят к мату
        candidate_moves = legal_moves
    elif board.is_check():
        # Если шах, добавляем все ходы, которые блокируют шах или уводят короля
        for move in legal_moves:
            board.push(move)
            if not board.is_check():
                candidate_moves.append(move)
            board.pop()
    else:
        # Взятие фигур
        for move in legal_moves:
            if board.is_capture(move):
                candidate_moves.append(move)

    # Если не найдены специфические ходы-кандидаты, возвращаем первый допустимый ход
    if not candidate_moves and legal_moves:
        candidate_moves.append(random.choice(legal_moves))

    # Восстановление правильного хода на доске
    board.turn = original_turn

    return candidate_moves

def find_candidate_moves_for_both_sides(board):
    white_moves = find_candidate_moves(board, chess.WHITE)
    black_moves = find_candidate_moves(board, chess.BLACK)
    return {'Белые': white_moves, 'Чёрные': black_moves}