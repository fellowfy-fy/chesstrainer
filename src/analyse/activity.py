import asyncio
import chess
import chess.engine
import pandas as pd


def evaluate_activity(board):
    metrics = {
        'Белые': {'Мобильность': 0, 'Агрессия': 0, 'Взаимодействие': 0, 'Территория': 0, 'Безопасность': 0, 'Централизация': 0},
        'Чёрные': {'Мобильность': 0, 'Агрессия': 0, 'Взаимодействие': 0, 'Территория': 0, 'Безопасность': 0, 'Централизация': 0}
    }
    
    for color in [chess.WHITE, chess.BLACK]:
        color_str = 'Белые' if color == chess.WHITE else 'Чёрные'
        
        # Обходим все типы фигур
        for piece_type in chess.PIECE_TYPES:
            for square in board.pieces(piece_type, color):
                moves = list(board.attacks(square))
                # Обрабатываем каждую возможную клетку, на которую может переместиться фигура
                for target_square in moves:
                    move = chess.Move(square, target_square)
                    if board.is_capture(move):
                        metrics[color_str]['Агрессия'] += 1
                    if board.piece_at(target_square) and board.piece_at(target_square).color != color:
                        metrics[color_str]['Взаимодействие'] += 1

                    metrics[color_str]['Мобильность'] += 1  # увеличиваем мобильность за каждый доступный ход
                    if board.piece_at(target_square) is None:
                        metrics[color_str]['Территория'] += 1  # клетка под контролем, если она пуста

                    if square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                        metrics[color_str]['Централизация'] += 1  # фигура в центре

                # Подсчет атакующих фигур для каждой фигуры
                attackers = board.attackers(not color, square)
                metrics[color_str]['Безопасность'] += len(attackers)

    return metrics
