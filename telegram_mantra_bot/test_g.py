import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("cred2.json", scope)
client = gspread.authorize(creds)

# Открываем таблицу по ID
spreadsheet_id = "1B3xNIJr39qy3UhiDyMqyfpjx8zbuFHnT-Wp5h3kUo0Y"
sheet = client.open_by_key(spreadsheet_id).sheet1

# Чтение данных
data = sheet.get_all_values()
print("Содержимое таблицы:")
for row in data:
    print(row)

# Запись данных
sheet.append_row(["Привет", "из", "Python!"])
print("✅ Данные записаны.")

