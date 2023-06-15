import requests
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_server_info(TOKEN):
    headers = {'Authorization': f'{TOKEN}'}
    response = requests.get('https://discord.com/api/users/@me/guilds', headers=headers)

    # Проверяем, что запрос был успешным
    if response.status_code != 200:
        print(f'Error {response.status_code}: {response.text}')
        return
    # Получаем список серверов, на которые подписан пользователь
    servers = json.loads(response.text)
    mas = []
    response = requests.get('https://discord.com/api/users/@me', headers=headers)
    if response.status_code == 200:
        user_id = response.json()["id"]
    else:
        user_id = "error in response"
    # Создаем файл для сохранения информации
    for server in servers:
        id = server['id']
        name = server['name']

        role_response = requests.get(f'https://discord.com/api/guilds/{id}/members/{user_id}', headers=headers)

        role_response_text = json.loads(role_response.text)
        joined_at = role_response_text["joined_at"]

        #convert date
        date = datetime.fromisoformat(joined_at)
        # Преобразование в формат dd.mm.yyyy
        date_formatted = date.strftime('%d.%m.%Y')

        if role_response.status_code == 200:
            # roles = [role['name'] for role in role_response.json()['roles']]
            roles = role_response_text["roles"]
        else:
            roles = [] #ошибка
            print(f'Error {role_response.status_code}: {role_response.text}')
            continue

        response = requests.get(f'https://discord.com/api/v9/guilds/{id}', headers=headers)

        print(response.text)

        if response.status_code != 200:
            role_names = {"error": "error in request"}
        else:
            server_info = json.loads(response.text)
            # Получаем информацию о ролях на сервере
            server_roles = server_info['roles']

            role_names = {}
            for role in server_roles:
                if role['id'] in roles:
                    role_names[role['id']] = role['name']

        roles_of_user = []
        for c in role_names.values():
            roles_of_user.append(c)

        #проверяем в тестовом элементе на наличие подмассивов если такие есть то преобразуем их содержимое в строку

        string_roles = ""
        for element in roles_of_user:
            string_roles += (" " + element)


        mas.append([id, name, date_formatted, string_roles, user_id])


    # Запись нового значения в ячейки
    return mas


def main():
    # Авторизация в Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # файл с ключом для доступа к api
    token_file_name_for_google_sheets = 's.json'

    creds = ServiceAccountCredentials.from_json_keyfile_name(token_file_name_for_google_sheets, scope)
    client = gspread.authorize(creds)

    # Открытие таблицы по URL
    # id вашей таблицы


    sheet_id = "1sk3SauxibXScq0FVy3s4KWHYkHHT0_seQrJm6ykbe30"


    sheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0'
    sheet = client.open_by_url(sheet_url).sheet1
    rows = sheet.get_all_values()

    rows = rows[1::]

    for row in rows:

        if type(row) == list:
            row = row[0]
        token = row.strip()
        if token != "":
            info = get_server_info(token)
        else:
            print("не корректный токен")
            continue
        line = 2
        try:
            for server_lines in info:
                sheet.update_acell(f'C{line}', token)
                sheet.update_acell(f'D{line}', server_lines[4])
                sheet.update_acell(f'E{line}', server_lines[0])
                sheet.update_acell(f'F{line}', server_lines[1])
                sheet.update_acell(f'G{line}', server_lines[2])
                sheet.update_acell(f'H{line}', server_lines[3])
                line += 1
        except:
            print(row)
            print("Ошибка")
            continue
if __name__ == "__main__":
    main()
