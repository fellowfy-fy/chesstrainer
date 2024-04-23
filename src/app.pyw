import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import chess
import chess.engine
import os
import pandas as pd
import random
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
from tabulate import tabulate

# Место для ваших функций анализа
from analyse.activity import evaluate_activity
from analyse.pawns_structure import analyze_pawns
from analyse.king_safety import evaluate_king_safety_for_both_sides
from analyse.material import evaluate_material
from analyse.flank_activity import analyze_flank_activity
from analyse.game_stage import determine_game_stage
from analyse.ideal_figure import evaluate_ideal_pieces
from analyse.dangerous_pawns import evaluate_dangerous_pawns
from analyse.candidate_moves import find_candidate_moves
from analyse.moves import generate_moves_table
from excel import save_df_to_excel, auto_adjust_columns, gather_metrics_data
# Путь к движку и загрузка данных
engine_path = os.path.join(os.path.dirname(__file__), "stockfish")

def format_dataframe(df):
    # Замена NaN на пустую строку

    # Преобразование DataFrame в строку с индексами и заголовками
    return df.to_string(header=False)
def update_gui_with_results(tab_control, results):
    global analysis_data
    analysis_data = results  # Сохраняем результаты для последующего использования
    for tab_name, data in results.items():
        # Поиск существующей вкладки по имени
        found = False
        for tab in tab_control.tabs():
            if tab_control.tab(tab, "text") == tab_name:
                text_widget = tab_control.nametowidget(tab).winfo_children()[0]
                text_widget.delete('1.0', tk.END)
                text_widget.insert(tk.END, data)
                found = True
                break
        
        # Если вкладка не найдена, создаем новую
        if not found:
            new_tab = ttk.Frame(tab_control)
            tab_control.add(new_tab, text=tab_name)
            text = tk.Text(new_tab)
            text.insert(tk.END, data)
            text.pack(expand=True, fill=tk.BOTH)

async def run_chess_analysis(engine_path, fen, canvas):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    transport, engine = await chess.engine.popen_uci(
        engine_path,
        startupinfo=si,  # Добавляем информацию о старте
        creationflags=subprocess.CREATE_NO_WINDOW  # Добавляем флаг для предотвращения появления окна
    )
    try:
        global board
        global FEN
        FEN = fen
        board = chess.Board(fen)
        info = await engine.analyse(board, chess.engine.Limit(depth=20))
        # Получите данные о доске и другие аналитические метрики
        activity_metrics = evaluate_activity(board)
        pawns_analysis = analyze_pawns(board)
        king_safety_metrics = evaluate_king_safety_for_both_sides(board)
        white_material, black_material = evaluate_material(board)
        flank_activity = analyze_flank_activity(board)
        stage = determine_game_stage(board)
        ideal_pieces = evaluate_ideal_pieces(board)
        dangerous_pawns = evaluate_dangerous_pawns(board)
        df_moves = generate_moves_table(board)
        candidate_moves = find_candidate_moves(board)
        draw_board(canvas, board)

        general_info = pd.DataFrame({
            "Метрика": {
            "Материал Белых": white_material,
            "Материал Чёрных": black_material,
            "Стадия": stage,
            "Ферзевый фланг": flank_activity["ферзевый фланг"],
            "Центр": flank_activity["центр"],
            "Королевский фланг": flank_activity["королевский фланг"],
            }
        }, columns = ['Метрика'])
        
        figures_info = pd.DataFrame({
            "Метрика":{
            "Идеальные фигуры Белые": [', '.join(ideal_pieces.get('Белые', []))],
            "Идеальные фигуры Чёрные": [', '.join(ideal_pieces.get('Чёрные', []))],
            "Опасные пешки Белые": [', '.join(dangerous_pawns.get('Белые', []))],
            "Опасные пешки Чёрные": [', '.join(dangerous_pawns.get('Чёрные', []))],
            "Ходы-кандидаты": candidate_moves  # Добавляем как единственную строку}
        }}, columns = ['Метрика'])
        return {
            "Активность": pd.DataFrame(activity_metrics, columns = ['Белые', 'Чёрные']),
            "Структура пешек": pd.DataFrame(pawns_analysis, columns = ['Белые', 'Чёрные']),
            "Безопасность короля": pd.DataFrame(king_safety_metrics),
            "Общая информация": general_info,
            "Фигуры": figures_info,
            "Ходы": df_moves,
        }
    finally:
        await engine.quit()

def run_analysis_in_thread(tab_control, engine_path, fen):
    # Создаём новый цикл событий
    loop = asyncio.new_event_loop()
    # Устанавливаем его в качестве текущего цикла событий в текущем потоке
    asyncio.set_event_loop(loop)
    # Запускаем асинхронную задачу в этом цикле
    results = loop.run_until_complete(run_chess_analysis(engine_path, fen, canvas))
    update_gui_with_results(tab_control, results)
    loop.close()  # Закрываем цикл после завершения работы


def paste_from_clipboard(fen_entry):
    try:
        fen_entry.delete(0, tk.END)
        fen_entry.insert(0, root.clipboard_get())
    except tk.TclError:
        messagebox.showerror("Paste Error", "Nothing to paste from clipboard")

def save_to_excel():
    global analysis_data
    try:
        fen_df = pd.DataFrame({"FEN": FEN}, index=[0])
        activity_df = analysis_data["Активность"].reset_index().rename(columns={'index': 'Параметр'})
        pawn_structure_df = analysis_data["Структура пешек"].reset_index().rename(columns={'index': 'Параметр'})
        king_safety_df = analysis_data["Безопасность короля"].reset_index().rename(columns={'index': 'Параметр'})
        general_info_df = analysis_data["Общая информация"].reset_index().rename(columns={'index': 'Параметр'})
        figures_info_df = analysis_data["Фигуры"].reset_index().rename(columns={'index': 'Параметр'})
        figures_info_df["Метрика"][4] = ', '.join(map(str, figures_info_df["Метрика"][4]))
        moves_df = analysis_data["Ходы"].reset_index(drop=True)
        
        
        # Сохранение данных в Excel
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
                save_df_to_excel(fen_df, writer, "FEN")
                activity_df.to_excel(writer, index=False, sheet_name="Активность")
                pawn_structure_df.to_excel(writer, index=False, sheet_name="Структура пешек")
                king_safety_df.to_excel(writer, index=False, sheet_name="Безопасность короля")
                general_info_df.to_excel(writer, index=False, sheet_name="Общая информация")
                figures_info_df.to_excel(writer, index=False, sheet_name="Фигуры")
                moves_df.to_excel(writer, index=False, sheet_name="Ходы")
                auto_adjust_columns(writer)
            messagebox.showinfo("Успех", f"Данные были успешно сохранены в {file_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при сохранении файла: {e}")



def setup_gui(root):
    fen_entry = ttk.Entry(root, width=50)
    fen_entry.pack(pady=5)

    paste_button = ttk.Button(root, text="Вставить из Буфера Обмена", command=lambda: paste_from_clipboard(fen_entry))
    paste_button.pack(pady=5)

    run_button = ttk.Button(root, text="Начать аналитику", command=lambda: run_analysis_in_thread(tab_control, engine_path, fen_entry.get()))
    run_button.pack(pady=5)

    candidate_move_button = ttk.Button(root, text="Сделать ход-кандидат", command=make_candidate_move_and_update_data)
    candidate_move_button.pack(pady=5)


    export_button = ttk.Button(root, text="Отправить в Excel", command=save_to_excel)
    export_button.pack(pady=5)
    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")


    return tab_control, fen_entry


def draw_board(canvas, board):
    canvas.delete("square")
    square_size = 30  # размер клетки
    font_size = 24  # новый уменьшенный размер шрифта
    colors = ["#f0d9b5", "#b58863"]
    emoji_map = {
        chess.Piece(chess.PAWN, chess.WHITE): '♙',
        chess.Piece(chess.KNIGHT, chess.WHITE): '♘',
        chess.Piece(chess.BISHOP, chess.WHITE): '♗',
        chess.Piece(chess.ROOK, chess.WHITE): '♖',
        chess.Piece(chess.QUEEN, chess.WHITE): '♕',
        chess.Piece(chess.KING, chess.WHITE): '♔',
        chess.Piece(chess.PAWN, chess.BLACK): '♟',
        chess.Piece(chess.KNIGHT, chess.BLACK): '♞',
        chess.Piece(chess.BISHOP, chess.BLACK): '♝',
        chess.Piece(chess.ROOK, chess.BLACK): '♜',
        chess.Piece(chess.QUEEN, chess.BLACK): '♛',
        chess.Piece(chess.KING, chess.BLACK): '♚',
    }
    for sq in chess.SQUARES:
        row, col = divmod(sq, 8)
        x0 = col * square_size
        y0 = (7 - row) * square_size
        x1 = x0 + square_size
        y1 = y0 + square_size
        color = colors[(row + col) % 2]
        canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill=color, tags="square")
        piece = board.piece_at(sq)
        if piece:
            emoji = emoji_map[piece]
            canvas.create_text(x0 + square_size / 2, y0 + square_size / 2, text=emoji, font=("Arial", font_size), tags="square")

def make_move_and_update_fen(board, move):
    try:
        move = chess.Move.from_uci(move)
        if move in board.legal_moves:
            board.push(move)
            return board.fen(), board
        else:
            messagebox.showinfo("Ошибка", "Недопустимый ход")
            return None, None
    except ValueError:
        messagebox.showinfo("Ошибка", "Некорректный формат хода")
        return None, None


def make_candidate_move_and_update_data():
    if not analysis_data["Фигуры"]["Метрика"]["Ходы-кандидаты"]:
        messagebox.showinfo("Ошибка", "Ходы-кандидаты не найдены")
        return
    try:
        # Предполагаем, что первый доступный ход-кандидат - это действительный ход
        candidate_move = random.choice(analysis_data["Фигуры"]["Метрика"]["Ходы-кандидаты"]).uci()
        new_fen, updated_board = make_move_and_update_fen(board, candidate_move)
        if new_fen:
            fen_entry.delete(0, tk.END)
            fen_entry.insert(0, new_fen)
            draw_board(canvas, updated_board)
            run_analysis_in_thread(tab_control, engine_path, new_fen)  # Перезапуск анализа с новой позицией
    except Exception as e:
        messagebox.showinfo("Ошибка", f"Ошибка при выполнении хода: {e}")

root = tk.Tk()
canvas = tk.Canvas(root, width=240, height=240)
canvas.pack()

fen_entry = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

loop = asyncio.get_event_loop()
loop.create_task(run_chess_analysis(engine_path, fen_entry, canvas))

tab_control, fen_entry = setup_gui(root)
root.mainloop()