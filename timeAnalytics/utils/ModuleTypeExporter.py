import openpyxl
import csv

# Define the path to your Excel file
excel_file_path = 'timeAnalytics/data/moduleIDs_WiSe24_25.xlsx'

# Load the workbook and select the active sheet
wb = openpyxl.load_workbook(excel_file_path)
sheet = wb.active

# Define the rows and their corresponding module types
module_types = {
    'Lernziel': 4,
    'Manuskript': 6,
    'Kurzuebersicht': 8,
    'Uebung': 10,
    'Quiz': 12,
    'Zusammenfassung': 14,
    'Zusatzmaterial Textuell': 16,
    'Zusatzmaterial Audio': 18,
    'Zusatzmaterial Visuell': 20
}

# Define the column range (D to BZ)
start_col = 'D'
end_col = 'BZ'

# Function to convert column letter to number
def col_letter_to_num(col):
    num = 0
    for char in col:
        num = num * 26 + (ord(char.upper()) - ord('A')) + 1
    return num

# Convert column letters to numbers
start_col_num = col_letter_to_num(start_col)
end_col_num = col_letter_to_num(end_col)

# Dictionary to hold the numbers grouped by module types
module_numbers = {key: [] for key in module_types.keys()}

# Fetch the numbers and group them by their module types
for module, row in module_types.items():
    for col in range(start_col_num, end_col_num + 1):
        cell_value = sheet.cell(row=row, column=col).value
        if cell_value:
            values = str(cell_value).split(',')
            for value in values:
                try:
                    number = int(value.strip())
                    module_numbers[module].append(number)
                except ValueError:
                    pass  # Ignore non-numeric values

# Print the grouped numbers (for verification)
for module, numbers in module_numbers.items():
    print(f"{module}: {numbers}")

# Save the grouped numbers to a CSV file
csv_file_path = 'timeAnalytics/data/grouped_module_numbers_wiSe_2425.csv'
with open(csv_file_path, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    for module, numbers in module_numbers.items():
        writer.writerow([module] + numbers)

print(f"Grouped module numbers saved to {csv_file_path}")
