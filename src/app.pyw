import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import chess
import chess.engine
import xlrd
import os
import pandas as pd
import random
import subprocess
import datetime
import xlwt

# Импорт функций анализа шахматной доски
from analyse.activity import evaluate_activity
from analyse.pawns_structure import analyze_pawns
from analyse.king_safety import evaluate_king_safety_for_both_sides
from analyse.material import evaluate_material
from analyse.flank_activity import analyze_flank_activity
from analyse.game_stage import determine_game_stage
from analyse.ideal_figure import evaluate_ideal_pieces
from analyse.dangerous_pawns import evaluate_dangerous_pawns
from analyse.candidate_moves import find_candidate_moves_for_both_sides, find_candidate_moves
from analyse.moves import generate_moves_table
# Путь к движку шахмат для анализа игры
engine_path = os.path.join(os.path.dirname(__file__), "stockfish")

def update_gui_with_results(tab_control, results):
    """ Обновление GUI с результатами анализа. """
    global analysis_data
    analysis_data = results  # Сохранение результатов для последующего использования
    for tab_name, data in results.items():
        found = False
        for tab in tab_control.tabs():
            if tab_control.tab(tab, "text") == tab_name:
                text_widget = tab_control.nametowidget(tab).winfo_children()[0]
                text_widget.delete('1.0', tk.END)
                text_widget.insert(tk.END, data)
                found = True
                break
        if not found:
            new_tab = ttk.Frame(tab_control)
            tab_control.add(new_tab, text=tab_name)
            text = tk.Text(new_tab)
            text.insert(tk.END, data)
            text.pack(expand=True, fill=tk.BOTH)

async def run_chess_analysis(engine_path, fen, canvas):
    """ Асинхронный запуск анализа шахматной партии. """
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE
    transport, engine = await chess.engine.popen_uci(
        engine_path, startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW
    )
    try:
        global board
        global FEN
        FEN = fen
        board = chess.Board(FEN)
        # Получение аналитических данных о текущем состоянии доски
        activity_metrics = evaluate_activity(board, figure_mapping)
        pawns_analysis = analyze_pawns(board)
        king_safety_metrics = evaluate_king_safety_for_both_sides(board)
        white_material, black_material = evaluate_material(board)
        flank_activity = analyze_flank_activity(board)
        stage = determine_game_stage(board)
        ideal_pieces = evaluate_ideal_pieces(board)
        dangerous_pawns = evaluate_dangerous_pawns(board)
        df_moves = generate_moves_table(board, figure_mapping)
        candidate_moves = find_candidate_moves_for_both_sides(board)
        # old_candidate_moves = find_candidate_moves(board, chess.WHITE)
        draw_board(canvas, board)
        # Сбор общей информации в DataFrame для вывода в GUI
        general_info = pd.DataFrame({
            "Метрика": {
                "Материал Белых": white_material,
                "Материал Чёрных": black_material,
                "Стадия": stage,
                "Ферзевый фланг": flank_activity["ферзевый фланг"],
                "Центр": flank_activity["центр"],
                "Королевский фланг": flank_activity["королевский фланг"],
            },
            "Единица": {
                "Материал Белых": "пш",
                "Материал Чёрных": "пш",
                "Стадия": "",
                "Ферзевый фланг": "",
                "Центр": "",
                "Королевский фланг": "",
            }
        }, columns = ['Метрика', "Единица"])
        # Организация данных о фигурах для отображения
        figures_info = pd.DataFrame({
            "Метрика":{
                "Идеальные фигуры Белые": [', '.join(ideal_pieces.get('Белые', []))],
                "Идеальные фигуры Чёрные": [', '.join(ideal_pieces.get('Чёрные', []))],
                "Опасные пешки Белые": [', '.join(dangerous_pawns.get('Белые', []))],
                "Опасные пешки Чёрные": [', '.join(dangerous_pawns.get('Чёрные', []))],
                # "Ходы-кандидаты Белые": [', '.join(map(str,candidate_moves.get('Белые', [])))], 
                # "Ходы-кандидаты Чёрные": [', '.join(map(str,candidate_moves.get('Чёрные', [])))],
                "Ходы-кандидаты Белые": candidate_moves.get('Белые', []),
                "Ходы-кандидаты Чёрные": candidate_moves.get('Чёрные', []),
            }
        }, columns = ['Метрика'])
        
        analyse_res = {
            "Активность": activity_metrics,
            "Структура пешек": pd.DataFrame(pawns_analysis, columns = ['Белые', 'Чёрные']),
            "Безопасность короля": pd.DataFrame(king_safety_metrics),
            "Общая информация": general_info,
            "Фигуры": figures_info,
            "Ходы": df_moves,
        }
        
        global candidate_moves_white, candidate_moves_black
        candidate_moves_white = analyse_res["Фигуры"]["Метрика"]["Ходы-кандидаты Белые"]
        candidate_moves_black = analyse_res["Фигуры"]["Метрика"]["Ходы-кандидаты Чёрные"]
        return analyse_res
    finally:
        await engine.quit()

def run_analysis_in_thread(tab_control, engine_path, fen):
    """ Запуск анализа в отдельном потоке для не блокирования GUI. """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(run_chess_analysis(engine_path, fen, canvas))
    update_gui_with_results(tab_control, results)
    loop.close()

def paste_from_clipboard(fen_entry):
    """ Вставка FEN из буфера обмена в текстовое поле. """
    try:
        fen_entry.delete(0, tk.END)
        fen_entry.insert(0, root.clipboard_get())
    except tk.TclError:
        messagebox.showerror("Paste Error", "Nothing to paste from clipboard")

def generate_filename():
    """ Генерирует уникальное имя файла на основе текущей даты и количества сохранений. """
    global save_counter, last_save_date
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().strftime("%H-%M-%S")
    return f"{current_date}_{current_time}/"


def generate_filename_xls():
    """ Генерирует уникальное имя файла на основе текущей даты и количества сохранений. """
    global save_counter, last_save_date
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().strftime("%H-%M-%S")
    return f"{current_date}_{current_time}.xls"

def generate_filename_csv():
    """ Генерирует уникальное имя файла на основе текущей даты и количества сохранений. """
    global save_counter, last_save_date
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().strftime("%H-%M-%S")
    return f"{current_date}_{current_time}.csv"


def create_sheet(workbook, sheet_name, df):
    """ Создание листа в книге и добавление данных из DataFrame """
    sheet = workbook.add_sheet(sheet_name)
    max_chars = 5000  # Максимальное количество символов для ширины столбца

    for col_idx, col in enumerate(df.columns):
        # Устанавливаем ширину столбца на основе максимальной длины данных в столбце
        column = df[col].astype(str)
        sheet.col(col_idx).width = max_chars

        # Добавляем заголовки столбцов
        sheet.write(0, col_idx, col)
        # Добавляем данные
        for row_idx, value in enumerate(column, start=1):
            sheet.write(row_idx, col_idx, value)


        
def on_paste(event, fen_entry):
    """ Обработчик нажатия Ctrl+V. """
    if (chr(event.keycode) == "V"):
        paste_from_clipboard(fen_entry)



def setup_gui(root):
    """ Настройка графического интерфейса пользователя. """
    style = ttk.Style()
    style.configure("Special.TButton", background="green", foreground="black", font=('Arial', 12))
    
    fen_entry = ttk.Entry(root, width=50)
    fen_entry.pack(pady=5)
    
    button_frame = ttk.Frame(root)
    button_frame.pack(fill='x', expand=True, padx=10, pady=10)

    paste_button = ttk.Button(button_frame, text="Вставить из Буфера Обмена", command=lambda: paste_from_clipboard(fen_entry))
    paste_button.pack(side='left', fill='x', expand=True, padx=5, pady=5)

    load_excel_button = ttk.Button(button_frame, text="Загрузить из Excel", command=lambda: load_from_excel(fen_entry))
    load_excel_button.pack(side='left', fill='x', expand=True, padx=5, pady=5)
    
    run_button = ttk.Button(button_frame, text="Начать аналитику", command=lambda: run_analysis_in_thread(tab_control, engine_path, fen_entry.get()), style="Special.TButton")
    run_button.pack(side='left', fill='x', expand=True, padx=5, pady=5)

    candidate_move_button = ttk.Button(button_frame, text="Сделать ход-кандидат", command=make_candidate_move_and_update_data)
    candidate_move_button.pack(side='left', fill='x', expand=True, padx=5, pady=5)

    export_button = ttk.Button(button_frame, text="Экспорт результатов", command=save_to_excel)
    export_button.pack(side='left', fill='x', expand=True, padx=5, pady=5)
    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both", padx=10, pady=10)
    
    
    return tab_control, fen_entry

def load_from_excel(fen_entry):
    """ Загрузка данных из Excel файла. """
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xls"), ("All files", "*.*")])
    if file_path:
        workbook = xlrd.open_workbook(file_path)
        sheet_fen = workbook.sheet_by_index(0)  # Первый лист для FEN записи
        sheet_figures = workbook.sheet_by_index(1)  # Второй лист для таблицы соответствия

        fen = sheet_fen.cell(0, 1).value  # Чтение FEN записи из ячейки A1
        for row_idx in range(sheet_figures.nrows):
            figure_name = sheet_figures.cell(row_idx, 0).value
            figure_position = sheet_figures.cell(row_idx, 1).value
            figure_mapping[figure_name] = figure_position
        fen_entry.delete(0, tk.END)
        fen_entry.insert(0, fen)  # Отображение FEN записи в поле ввода
        messagebox.showinfo("Загрузка завершена", "FEN и соответствие фигур загружены")


def draw_board(canvas, board):
    """ Отрисовка шахматной доски. """
    canvas.delete("square")
    square_size = 30  # размер клетки
    font_size = 24  # размер шрифта
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



# Инвертированный словарь, где ключами являются позиции, а значениями — альтернативные имена

def save_to_excel():
    """ Сохранение результатов анализа в Excel файл с автоматически сгенерированным именем в папке 'Партии'. """
    file_name = generate_filename_xls()  # Функция для генерации имени файла
    directory = "Сессии" + "/" + generate_filename()  # Имя папки для сохранения
    if not os.path.exists(directory):
        os.makedirs(directory)  # Создать папку, если она не существует
    file_path = os.path.join(directory, file_name)
    global analysis_data
    export_moves_to_csv(board, candidate_moves_white, candidate_moves_black, directory)
    try:
        

        workbook = xlwt.Workbook()  # Создаем книгу в формате xls
        # Создаем листы и добавляем данные с автоматической настройкой ширины столбцов
        create_sheet(workbook, "FEN", pd.DataFrame({"FEN": FEN}, index=[0]))
        activity_df = analysis_data["Активность"].reset_index()
        create_sheet(workbook, "Активность", activity_df)
        create_sheet(workbook, "Структура пешек", analysis_data["Структура пешек"].reset_index().rename(columns={'index': 'Параметр'}))
        create_sheet(workbook, "Безопасность короля", analysis_data["Безопасность короля"].reset_index().rename(columns={'index': 'Параметр'}))
        create_sheet(workbook, "Общая информация", analysis_data["Общая информация"].reset_index().rename(columns={'index': 'Параметр'}))
        figures_info_df = analysis_data["Фигуры"].reset_index().rename(columns={'index': 'Параметр'})
        figures_info_df['Метрика'][4] = ', '.join(map(str, figures_info_df['Метрика'][4]))
        figures_info_df['Метрика'][5] = ', '.join(map(str, figures_info_df['Метрика'][5]))
        create_sheet(workbook, "Фигуры", figures_info_df)
        create_sheet(workbook, "Ходы", analysis_data["Ходы"].reset_index(drop=True))
        
        workbook.save(file_path)  # Сохраняем книгу
        messagebox.showinfo("Успех", f"Данные были успешно сохранены в {file_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при сохранении файла: {e}")

def get_piece_name(piece, square):
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

def get_priority(move, board, candidate_moves):

    piece = board.piece_at(move.from_square)
    piece_priority = {
        chess.KING: 3,
        chess.QUEEN: 4,
        chess.KNIGHT: 5,
        chess.ROOK: 6,
        chess.BISHOP: 7,
        chess.PAWN: 8
    }
    if move in candidate_moves:
        if candidate_moves.index(move) == 0 or candidate_moves.index(move) == 1:
            return candidate_moves.index(move) + 1
    
    return piece_priority.get(piece.piece_type, 100)


def export_moves_to_csv(board, candidate_moves_white, candidate_moves_black, directory):
    moves_data = []
    file_name = generate_filename_csv()  # Функция для генерации имени файла
    file_path = os.path.join(directory, file_name)

    for color, candidate_moves in [(chess.WHITE, candidate_moves_white), (chess.BLACK, candidate_moves_black)]:
        board.turn = color  # Устанавливаем ход нужного цвета
        all_pieces = {square: board.piece_at(square) for piece_type in chess.PIECE_TYPES for square in board.pieces(piece_type, color)}

        for square, piece in all_pieces.items():
            from_square = chess.square_name(square)
            legal_moves = [move for move in board.legal_moves if move.from_square == square]

            # Если у фигуры нет легальных ходов, добавляем запись с пустыми значениями
            if not legal_moves:
                move_info = {
                    "Имя": get_piece_name(piece, from_square),
                    "Тип": 1 if color == chess.WHITE else 2,
                    "Состояние 1": from_square,
                    "Состояние 2": "",
                    "Условие": "",
                    "Приоритет": 100  # Приоритет для фигур без ходов
                }
                moves_data.append(move_info)

            # Обработка легальных ходов
            for move in legal_moves:
                to_square = chess.square_name(move.to_square)
                captured_piece = board.piece_at(move.to_square)
                priority = get_priority(move, board, candidate_moves)

                move_info = {
                    "Имя": get_piece_name(piece, from_square),
                    "Тип": 1 if color == chess.WHITE else 2,
                    "Состояние 1": from_square,
                    "Состояние 2": to_square,
                    "Условие": get_piece_name(captured_piece, to_square) if captured_piece else '',
                    "Приоритет": priority
                }
                moves_data.append(move_info)

    # Сортировка по типу и приоритету перед экспортом
    moves_data.sort(key=lambda x: (x['Тип'], x['Приоритет']))
    
    for index, move in enumerate(moves_data, 1):# начинаем с 1 для номера строки в CSV
        attacked = move['Условие']
        attacked2 = move['Состояние 2']
        for index, move2 in enumerate(moves_data, 1):
            if move2["Имя"] == attacked and move2["Состояние 1"] == attacked2:
                move['Условие'] = f"{index + 1}"
        

    
    df = pd.DataFrame(moves_data)
    df.to_csv(file_path, index=False, sep=';')

def make_move_and_update_fen(board, move):
    """ Выполнение хода и обновление FEN. """
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
    try:
        if board.turn == False:
            candidate_move = random.choice(analysis_data["Фигуры"]["Метрика"]["Ходы-кандидаты Чёрные"]).uci()
        else:
            candidate_move = random.choice(analysis_data["Фигуры"]["Метрика"]["Ходы-кандидаты Белые"]).uci()
        new_fen, updated_board = make_move_and_update_fen(board, candidate_move)
        if new_fen:
            fen_entry.delete(0, tk.END)
            fen_entry.insert(0, new_fen)
            draw_board(canvas, updated_board)
            run_analysis_in_thread(tab_control, engine_path, new_fen)
    except Exception as e:
        messagebox.showinfo("Ошибка", f"Ошибка при выполнении хода: {e}")

root = tk.Tk()
root.geometry('800x600')
root.bind('<Key>', lambda event: on_paste(event, fen_entry))
canvas = tk.Canvas(root, width=240, height=240)
canvas.pack()

global figure_mapping
figure_mapping = {}
fen_entry = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

loop = asyncio.get_event_loop()
loop.create_task(run_chess_analysis(engine_path, fen_entry, canvas))

tab_control, fen_entry = setup_gui(root)
root.mainloop()