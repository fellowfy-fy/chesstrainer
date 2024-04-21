import pandas as pd



def save_df_to_excel(df, writer, sheet_name):
    # Запись DataFrame на указанный лист, используя предоставленный ExcelWriter
    df.to_excel(writer, sheet_name=sheet_name, index=False)
