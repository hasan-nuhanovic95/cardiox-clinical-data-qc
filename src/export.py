import pandas as pd
from pathlib import Path
from src.config import OUTPUT_FILE


def export_review_workbook(
        sheets: dict[str, pd.DataFrame], output_file: str | Path = OUTPUT_FILE) -> None:
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        for sheet in writer.sheets.values():
            for column_cells in sheet.columns:
                column_letter = column_cells[0].column_letter
                sheet.column_dimensions[column_letter].width = 18

            for row in sheet.iter_rows(min_row=2):
                for cell in row:
                    if cell.is_date:
                        cell.number_format = "yyyy-mm-dd"
