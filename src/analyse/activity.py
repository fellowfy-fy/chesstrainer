import chess

# Подключаем библиотеку для работы с шахматами
import pandas as pd

# Вспомогательная функция для получения названия фигуры
def get_piece_name(piece, square, figure_mapping):
    """ Возвращает альтернативное название фигуры или стандартное, основываясь на позиции. """
    if piece is None:
        return ''
    # Словарь стандартных названий фигур
    standard_names = {
        chess.PAWN: 'Пешка',
        chess.KNIGHT: 'Конь',
        chess.BISHOP: 'Слон',
        chess.ROOK: 'Ладья',
        chess.QUEEN: 'Ферзь',
        chess.KING: 'Король'
    }
    standard_name = standard_names.get(piece.piece_type, 'Неизвестно')
    square_name = square
    # Проверяем, содержится ли текущая позиция в значении словаря figure_mapping
    for name, pos in figure_mapping.items():
        if pos == square_name:
            return name  # Возвращаем альтернативное название, если нашли совпадение
    return standard_name  # Возвращаем стандартное название, если не нашли совпадений

# Функция для анализа деятельности на доске
def evaluate_activity(board, figure_mapping):
    categories = ['Мобильность', 'Агрессия', 'Взаимодействие', 'Территория', 'Безопасность', 'Централизация']
    activity = {category: {'Белые': [], 'Чёрные': []} for category in categories}

    for color in [chess.WHITE, chess.BLACK]:
        board.turn = color
        color_str = 'Белые' if color == chess.WHITE else 'Чёрные'

        for piece_type in chess.PIECE_TYPES:
            for square in board.pieces(piece_type, color):
                piece = board.piece_at(square)
                square_name = chess.square_name(square)
                piece_name = get_piece_name(piece, square_name, figure_mapping)
                moves = [move for move in board.legal_moves if move.from_square == square]

                descriptions = {
                    'Мобильность': f"{piece_name} {chess.square_name(square)} – {len(moves)} клеток",
                    'Агрессия': [f"{piece_name} {chess.square_name(square)} нападает на {get_piece_name(board.piece_at(m.to_square), chess.square_name(m.to_square), figure_mapping)} {chess.square_name(m.to_square)}" for m in moves if board.is_capture(m)],
                    'Взаимодействие': evaluate_interaction(board, figure_mapping, color, square),
                    'Территория': evaluate_territory(board, color, square, figure_mapping),
                    'Безопасность': evaluate_security(board, color, square, figure_mapping),
                    'Централизация': f"{piece_name} {chess.square_name(square)} – {'да' if square in [chess.D4, chess.E4, chess.D5, chess.E5] else 'нет'}"
                }

                for key in descriptions:
                    if isinstance(descriptions[key], list):
                        descriptions[key] = "\n".join(descriptions[key])
                    activity[key][color_str].append(descriptions[key])

    
    max_length = max(len(lst) for cat in activity.values() for lst in cat.values())
    for cat in activity.values():
        for color_list in cat.values():
            color_list.extend([""] * (max_length - len(color_list)))
    
    # Конвертируем активность в DataFrame
    activity_df = pd.DataFrame({(outerKey, innerKey): values for outerKey, innerDict in activity.items() for innerKey, values in innerDict.items()})
    return activity_df.transpose()


def evaluate_interaction(board, figure_mapping, color, square):
    defenders = board.attackers(color, square)
    piece = board.piece_at(square)
    piece_name = get_piece_name(piece, square, figure_mapping)
    square_name = chess.square_name(square)
    interaction = ""
    if defenders:
        defended_by = []
        for defender in defenders:
            if defender != square:  # Исключаем самозащиту фигуры
                defender_piece = board.piece_at(defender)
                defending_piece_name = get_piece_name(defender_piece, defender, figure_mapping)
                defending_square_name = chess.square_name(defender)
                defended_by.append(f"{defending_piece_name} {defending_square_name}")
        
        if defended_by:
            interaction = f"{piece_name} {square_name} защищен " + ", ".join(defended_by)
    
    return interaction

def evaluate_security(board, color, square, figure_mapping):
    attack_str = ""
    enemy_color = not color
    attackers = board.attackers(enemy_color, square)
    piece = board.piece_at(square)
    if attackers:
        attacked_piece_name = get_piece_name(piece, square, figure_mapping)
        attacked_square_name = chess.square_name(square)
        attackers_info = []

        for attacker in attackers:
            attacker_name = board.piece_at(attacker)
            attacking_piece_name = get_piece_name(attacker_name, attacker, figure_mapping)
            attacking_square_name = chess.square_name(attacker)
            attackers_info.append(f"{attacking_piece_name} {attacking_square_name}")

        if attackers_info:
            attack_str = f"{attacked_piece_name} {attacked_square_name} – атакован {', '.join(attackers_info)}"

    return attack_str

def evaluate_territory(board, color, square, figure_mapping):

    own_territory_rows = range(0, 4) if color == chess.WHITE else range(4, 8)
    piece = board.piece_at(square)
    piece_name = get_piece_name(piece, square, figure_mapping)
    row = chess.square_rank(square)
    territory_status = 'своя' if row in own_territory_rows else 'чужая'
    square_name = chess.square_name(square)
    territory_info = f"{piece_name} {square_name} – {territory_status}"

    return territory_info