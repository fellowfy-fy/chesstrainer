import asyncio
import random
import chess
import chess.engine
import pandas as pd
import os
from analyse.activity import evaluate_activity
from analyse.pawns_structure import analyze_pawns
from excel import save_df_to_excel, auto_adjust_columns
from analyse.king_safety import evaluate_king_safety_for_both_sides
from analyse.material import evaluate_material
from analyse.flank_activity import analyze_flank_activity
from analyse.game_stage import determine_game_stage
from analyse.ideal_figure import evaluate_ideal_pieces
from analyse.dangerous_pawns import evaluate_dangerous_pawns
from analyse.candidate_moves import find_candidate_moves

if os.path.exists('chess_metrics.xlsx'):
    df = pd.read_excel('chess_metrics.xlsx')
else:
    df = pd.read_excel('chess_metrics.xls')
FEN = df.at[0, 'FEN']
engine_path = os.path.join(os.path.dirname(__file__), "stockfish.exe")


def generate_moves_table(board):
    moves_white = []
    moves_black = []

    # Сохраняем текущую позицию для возврата после генерации ходов
    snapshot = board.fen()

    # Генерация ходов для белых
    board.turn = chess.WHITE
    for move in board.legal_moves:
        board.push(move)
        moves_white.append(f"{board.piece_at(move.to_square).symbol()} {chess.square_name(move.from_square)} -> {chess.square_name(move.to_square)}")
        board.pop()

    # Генерация ходов для черных
    board.turn = chess.BLACK
    for move in board.legal_moves:
        board.push(move)
        moves_black.append(f"{board.piece_at(move.to_square).symbol()} {chess.square_name(move.from_square)} -> {chess.square_name(move.to_square)}")
        board.pop()

    # Возвращаем доску в исходное состояние
    board.set_fen(snapshot)

    # Создание DataFrame
    max_len = max(len(moves_white), len(moves_black))
    if len(moves_white) < max_len:
        moves_white.extend([""] * (max_len - len(moves_white)))
    if len(moves_black) < max_len:
        moves_black.extend([""] * (max_len - len(moves_black)))

    df = pd.DataFrame({
        'Белые': moves_white,
        'Чёрные': moves_black
    })

    return df


def gather_metrics_data(ideal_pieces, dangerous_pawns, candidate_moves, board):
    # Сбор данных в структурированный список для создания DataFrame
    data = {
        "Категория": [],
        "Значение": []
    }
    
    # Идеальные фигуры
    for color, pieces in ideal_pieces.items():
        data["Категория"].append(f"Идеальные фигуры {color.capitalize()}")
        data["Значение"].append(', '.join(pieces))
    
    # Опасные пешки
    for color, pawns in dangerous_pawns.items():
        data["Категория"].append(f"Опасные пешки {color.capitalize()}")
        data["Значение"].append(', '.join(pawns))
    
    # Ходы-кандидаты
    data["Категория"].append("Ходы-кандидаты")
    data["Значение"].append(', '.join([board.san(move) for move in candidate_moves]))
    
    return pd.DataFrame(data, columns=['Категория', 'Значение'])



async def main():
    transport, engine = await chess.engine.popen_uci(engine_path)
    try:
        board = chess.Board(FEN)
        info = await engine.analyse(board, chess.engine.Limit(depth=20))
        
        # Получение метрик
        activity_metrics = evaluate_activity(board)
        pawns_analysis = analyze_pawns(board)
        king_safety_metrics = evaluate_king_safety_for_both_sides(board)
        white_material, black_material = evaluate_material(board)
        flank_activity = analyze_flank_activity(board)
        stage = determine_game_stage(board)
        ideal_pieces = evaluate_ideal_pieces(board)
        print("Ideal pieces based on deep analysis:")
        for color, pieces in ideal_pieces.items():
            print(f"{color.capitalize()}: {', '.join(pieces)}")
        dangerous_pawns = evaluate_dangerous_pawns(board)
        print("Dangerous pawns:")
        for color, pawns in dangerous_pawns.items():
            print(f"{color.capitalize()}: {', '.join(pawns)}")
        df_moves = generate_moves_table(board)
        
            
        candidate_moves = find_candidate_moves(board)
        print("Ходы кандидаты:", [board.san(move) for move in candidate_moves])
            
        # while not board.is_game_over():
        #     candidate_moves = find_candidate_moves(board)
        #     print("Candidate Moves:", [board.san(move) for move in candidate_moves])

        #     # Пример: Выбираем случайный ход-кандидат
        #     if candidate_moves:
        #         move = random.choice(candidate_moves)
        #         board.push(move)
        #     else:
        #         break
        # Создание DataFrame из каждого набора метрик
        print(df_moves)
        activity_data = {
            "Параметр": [],
            "Белые": [],
            "Чёрные": []
        }
        for key in activity_metrics['Белые']:
            activity_data["Параметр"].append(key)
            activity_data["Белые"].append(activity_metrics['Белые'][key])
            activity_data["Чёрные"].append(activity_metrics['Чёрные'][key])
        
        # Обработка данных пешечной структуры
        pawn_structure_data = {
            "Параметр": [],
            "Белые": [],
            "Чёрные": []
        }
        for metric, values in pawns_analysis['Белые'].items():
            pawn_structure_data["Параметр"].append(metric)
            pawn_structure_data["Белые"].append(', '.join(values))
            pawn_structure_data["Чёрные"].append(', '.join(pawns_analysis['Чёрные'][metric]))
            
        king_safety_data = {
            "Параметр": [],
            "Белые": [],
            "Чёрные": []
        }
        
        for key in king_safety_metrics['Белые']:
            king_safety_data["Параметр"].append(key)
            king_safety_data["Белые"].append(king_safety_metrics['Белые'][key])
            king_safety_data["Чёрные"].append(king_safety_metrics['Чёрные'][key])
            
            
        fen_df = pd.DataFrame({"FEN": FEN}, index=[0])
        activity_df = pd.DataFrame(activity_data)
        pawn_structure_df = pd.DataFrame(pawn_structure_data)
        king_safety_df = pd.DataFrame(king_safety_data)
        data_items = list(flank_activity.items()) + [('Стадия', stage), ('Белые', white_material), ('Чёрные', black_material)]
        flank_df = pd.DataFrame(data_items, columns=['Категория', 'Значение'])
        df_metrics = gather_metrics_data(ideal_pieces, dangerous_pawns, candidate_moves, board)
        # Сохранение всех DataFrame в один файл Excel с разными листами
        
        if os.path.exists('chess_metrics.xlsx'):
            with pd.ExcelWriter("chess_metrics.xlsx", engine='openpyxl', mode='w') as writer:
                save_df_to_excel(fen_df, writer, "FEN")
                save_df_to_excel(activity_df, writer, "Активность")
                save_df_to_excel(pawn_structure_df, writer, "Структура пешек")
                save_df_to_excel(king_safety_df, writer, "Безопасность короля")
                save_df_to_excel(flank_df, writer, "Стратегия")
                save_df_to_excel(df_metrics, writer, sheet_name="Анализ")
                save_df_to_excel(df_moves, writer, "Ходы")
                auto_adjust_columns(writer)
        else:
            with pd.ExcelWriter("chess_metrics.xls", engine='openpyxl', mode='w') as writer:
                save_df_to_excel(fen_df, writer, "FEN")
                save_df_to_excel(activity_df, writer, "Активность")
                save_df_to_excel(pawn_structure_df, writer, "Структура пешек")
                save_df_to_excel(king_safety_df, writer, "Безопасность короля")
                save_df_to_excel(flank_df, writer, "Стратегия")
                save_df_to_excel(df_metrics, writer, sheet_name="Анализ")
                save_df_to_excel(df_moves, writer, "Ходы")
                auto_adjust_columns(writer)
    finally:
        await engine.quit()

asyncio.run(main())