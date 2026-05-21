import os

from openpyxl import Workbook

def export_to_excel(messages):
    workbook = Workbook()
    
    sheet = workbook.active
    
    sheet.title = "Chat History"
    sheet.append(["Chat #", "Question", "Answer", "Citations"])

    for index, message in enumerate(messages, start=1):
        citations = "\n".join(message["citations"]) if message["citations"] else "No citations."

        sheet.append([
            index,
            message["question"],
            message["answer"],
            citations,
        ])

    sheet.column_dimensions["A"].width = 10
    sheet.column_dimensions["B"].width = 40
    sheet.column_dimensions["C"].width = 60
    sheet.column_dimensions["D"].width = 50
    
    output_path = "exports/response.xlsx"

    os.makedirs("exports", exist_ok=True)
    
    workbook.save(output_path)
    
    return output_path
    
    
