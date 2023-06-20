from time import sleep
import requests
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#id ваших таблиц

#для сохранения информации о серверах
sheet_servers_id = "1QU95zOjy4TSVReB7LRu1-BMOGa6zKxt4wf7l-OQmHtY"

#для сохранения информации аккаунтов
sheet_accounts_id = "1P-8crhcmSo_0pl_Ii_dniQ40hMGFzcr7Nd9v8dXmrq8"

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

    #получить больше информации о пользователе

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

        # получить всю информацию о сервере ....

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
            string_roles += ("," + element)

        string_roles = string_roles.strip()

        if string_roles.startswith(","):
            string_roles = string_roles[1::]
        if string_roles.endswith(","):
            string_roles = string_roles[:len(string_roles) - 1]

        mas.append([user_id, id, name, date_formatted, string_roles])


    # Запись нового значения в ячейки
    return mas

def get_account_info(TOKEN):
    headers = {'Authorization': f'{TOKEN}'}
    response = requests.get('https://discord.com/api/users/@me', headers=headers)

    user_info_dict = response.json()

    user_info_data = []
    header = ['id', 'username', 'global_name', 'avatar', 'discriminator', 'public_flags', 'flags', 'banner','banner_color', 'accent_color', 'bio', 'locale', 'nsfw_allowed', 'mfa_enabled','premium_type', 'linked_users', 'avatar_decoration', 'email', 'verified', 'phone']

    if response.status_code == 200:
        #"Загловок для таблицы с данными пользователя"

        for key in header:
            try:
                val = user_info_dict[key]
            except:
                val = ""



            if type(val) == list:
                val = ','.join(val)
            if val == 'null':
                val = ""

            user_info_data.append(val)

    else:
        print("error in response")
    return user_info_data

    # получить больше информации о пользователе
def table_with_servers():
    # Авторизация в Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # файл с ключом для доступа к api
    token_file_name_for_google_sheets = 's.json'

    creds = ServiceAccountCredentials.from_json_keyfile_name(token_file_name_for_google_sheets, scope)
    client = gspread.authorize(creds)

    # Открытие таблицы по URL

    sheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_servers_id}/edit#gid=0'
    sheet = client.open_by_url(sheet_url).sheet1
    rows = sheet.get_all_values()
    rows = rows[1::]

    range_to_clear = 'C2:Z1000'
    sheet.batch_clear([range_to_clear])

    for row in rows:

        if type(row) == list:
            row = row[0]
        token = row.strip()


        if token != "":
            print()
            print(f"обработка токена {token} ..... ")
            try:
                info = get_server_info(token)
                line = 2
                print(f"Вставка токена {token} .... в таблицу серверов с id {sheet_servers_id} ")
                try:
                    for element in info:
                        element = [token] + element
                        sheet.append_row(element, table_range=f"C{line}")
                        line += 1
                        sleep(1)
                except:
                    print("Произошла ошибка, превышено допустимое количество запросов к Google API")
                    continue
            except:
                print("Произошла ошибка, возможно ваш токен не действителен")
        else:
            #print("пустой токен")
            continue

        sleep(2)
    #возвращаем список токенов из первой таблицы для заполнения второй
    mas_tokens = []
    for row in rows:

        if type(row) == list:
            row = row[0]
        token = row.strip()
        mas_tokens.append(token)
    return mas_tokens

def table_with_account(tokens):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # файл с ключом для доступа к api
    token_file_name_for_google_sheets = 's.json'

    creds = ServiceAccountCredentials.from_json_keyfile_name(token_file_name_for_google_sheets, scope)
    client = gspread.authorize(creds)

    # Открытие таблицы по URL
    
    sheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_accounts_id}/edit#gid=0'
    sheet = client.open_by_url(sheet_url).sheet1

    header = ['token', 'id', 'username', 'global_name', 'avatar', 'discriminator', 'public_flags', 'flags', 'banner', 'banner_color', 'accent_color', 'bio', 'locale', 'nsfw_allowed', 'mfa_enabled', 'premium_type', 'linked_users', 'avatar_decoration', 'email', 'verified', 'phone']
    range_to_clear = 'A1:Z1000'
    sheet.batch_clear([range_to_clear])
    sheet.append_row(header, table_range=f"A{1}")



    line = 2
    for token in tokens:
        if token != "":
            print()
            print(f"получение данных аккаунта токена {token} ....")
            try:
                user_data = get_account_info(token)
                try:
                    print(f"Вставка данных аккаунта токена {token} .... в таблицу аккаунтов с id {sheet_accounts_id} ")
                    sheet.append_row([token] + user_data, table_range=f"A{line}")
                    line += 1
                    sleep(2)
                except:
                    print("ошибка, превышено количество запросов к Google API")
            except:
                print(f"токен {token} не корректен")
        else:
            continue
        sleep(2)

if __name__ == "__main__":
    print("--------------------------")
    print("Создание таблицы серверов")
    print("--------------------------")

    tokens = table_with_servers()
    
    print("--------------------------")
    print("Создание таблицы аккаунтов")
    print("--------------------------")

    table_with_account(tokens)
