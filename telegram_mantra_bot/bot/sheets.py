from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import List, Dict, Any
import os
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Константы для работы с Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_ID')
USERS_RANGE = 'Users!A1:Z'  # Для гибкой работы с колонками
G_CRED = 'cred2.json'

class GoogleSheetsClient:
    def __init__(self):
        try:
            credentials = Credentials.from_service_account_file(
                G_CRED,
                scopes=SCOPES
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            self.sheet = self.service.spreadsheets()
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            raise

    def get_all_messages(self) -> Dict[str, str]:
        try:
            result = self.sheet.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range='keys!A2:C'
            ).execute()
            values = result.get('values', [])
            return {row[0]: row[1] for row in values if len(row) >= 2}
        except Exception as e:
            logger.error(f"Failed to get messages from Google Sheets: {e}")
            return {}

    # --- Гибкая работа с Users ---
    def get_users_headers_and_rows(self):
        result = self.sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=USERS_RANGE
        ).execute()
        values = result.get('values', [])
        if not values:
            return [], []
        headers = values[0]
        rows = values[1:]
        return headers, rows

    def get_column_index(self, headers, column_name):
        try:
            return headers.index(column_name)
        except ValueError:
            return -1

    def add_or_update_user(self, user: dict):
        headers, rows = self.get_users_headers_and_rows()
        if not headers:
            logger.error("Users sheet is missing headers!")
            return False
        user_id_idx = self.get_column_index(headers, 'user_id')
        if user_id_idx == -1:
            logger.error("No 'user_id' column in Users sheet!")
            return False
        user_ids = [row[user_id_idx] for row in rows if len(row) > user_id_idx]
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        if str(user['user_id']) in user_ids:
            idx = user_ids.index(str(user['user_id']))
            row_num = idx + 2
            updates = {}
            for field in ['last_active', 'username', 'first_name', 'last_name']:
                col_idx = self.get_column_index(headers, field)
                if col_idx != -1:
                    col_letter = chr(ord('A') + col_idx)
                    value = now if field == 'last_active' else user.get(field, '')
                    updates[field] = (col_letter, value)
            for field, (col_letter, value) in updates.items():
                self.sheet.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f'Users!{col_letter}{row_num}',
                    valueInputOption='RAW',
                    body={'values': [[value]]}
                ).execute()
        else:
            row = [''] * len(headers)
            for k, v in user.items():
                idx = self.get_column_index(headers, k)
                if idx != -1:
                    row[idx] = v
            started_at_idx = self.get_column_index(headers, 'started_at')
            last_active_idx = self.get_column_index(headers, 'last_active')
            if started_at_idx != -1:
                row[started_at_idx] = now
            if last_active_idx != -1:
                row[last_active_idx] = now
            self.sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=USERS_RANGE,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row]}
            ).execute()
        return True

    def save_questions_block(self, user_id: int, questions_and_answers: list):
        headers, rows = self.get_users_headers_and_rows()
        if not headers:
            logger.error("Users sheet is missing headers!")
            return False
        user_id_idx = self.get_column_index(headers, 'user_id')
        col_idx = self.get_column_index(headers, 'questions')
        if user_id_idx == -1 or col_idx == -1:
            logger.error("No 'user_id' or 'questions' column in Users sheet!")
            return False
        user_ids = [row[user_id_idx] for row in rows if len(row) > user_id_idx]
        block = "\n".join([f"{q}:\n{a}" for q, a in questions_and_answers])
        if str(user_id) in user_ids:
            idx = user_ids.index(str(user_id))
            row_num = idx + 2
            col_letter = chr(ord('A') + col_idx)
            # Получаем текущее значение и дописываем
            try:
                current = rows[idx][col_idx] if len(rows[idx]) > col_idx else ''
            except Exception:
                current = ''
            new_block = (current + '\n' if current else '') + block
            self.sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'Users!{col_letter}{row_num}',
                valueInputOption='RAW',
                body={'values': [[new_block]]}
            ).execute()
            return True
        else:
            logger.error(f"User {user_id} not found in Users sheet!")
            return False

    def save_ai_result(self, user_id: int, result: str):
        headers, rows = self.get_users_headers_and_rows()
        if not headers:
            logger.error("Users sheet is missing headers!")
            return False
        user_id_idx = self.get_column_index(headers, 'user_id')
        col_idx = self.get_column_index(headers, 'ai_result')
        if user_id_idx == -1 or col_idx == -1:
            logger.error("No 'user_id' or 'ai_result' column in Users sheet!")
            return False
        user_ids = [row[user_id_idx] for row in rows if len(row) > user_id_idx]
        if str(user_id) in user_ids:
            idx = user_ids.index(str(user_id))
            row_num = idx + 2
            col_letter = chr(ord('A') + col_idx)
            self.sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'Users!{col_letter}{row_num}',
                valueInputOption='RAW',
                body={'values': [[result]]}
            ).execute()
            return True
        else:
            logger.error(f"User {user_id} not found in Users sheet!")
            return False

# Глобальный экземпляр клиента
sheets_client = None

def init_sheets_client():
    global sheets_client
    try:
        sheets_client = GoogleSheetsClient()
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets client: {e}")
        return False

def get_message(message_key: str) -> str:
    if not sheets_client:
        return None
    messages = sheets_client.get_all_messages()
    return messages.get(message_key)

def add_or_update_user(user: dict):
    if not sheets_client:
        return False
    return sheets_client.add_or_update_user(user)

def save_questions_block(user_id: int, questions_and_answers: list):
    if not sheets_client:
        return False
    return sheets_client.save_questions_block(user_id, questions_and_answers)

def save_ai_result(user_id: int, result: str):
    if not sheets_client:
        return False
    return sheets_client.save_ai_result(user_id, result) 