import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows
from tkinter import  filedialog, messagebox

def save_to_excel(analysis_data):
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
                fen_df.to_excel(writer, index=False, sheet_name="FEN")
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



def auto_adjust_columns(sheet, df):
    for col_idx, col in enumerate(df.columns):
        # Находим максимальную ширину содержимого столбца
        max_len = max((len(str(x)) for x in df[col]), default=0)
        max_len = max(max_len, len(str(col)))  # Учитываем длину заголовка столбца
        sheet.col(col_idx).width = max_len * 367  # 367 - примерное значение для ширины символа в Excel


