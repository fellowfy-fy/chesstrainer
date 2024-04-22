import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def save_df_to_excel(df, writer, sheet_name):
    # Запись DataFrame на указанный лист, используя предоставленный ExcelWriter
    df.to_excel(writer, sheet_name=sheet_name, index=False)


def auto_adjust_columns(writer):
    for sheetname in writer.sheets:
        worksheet = writer.sheets[sheetname]
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter  # Get the column name
            for cell in col:
                try:  # Necessary to avoid error on empty cells
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            worksheet.column_dimensions[column].width = adjusted_width
