import sqlite3 as sq
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = 'creds.json'  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])


def update_catalog():
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    spreadsheetId = '1qE0RqXxh05uXJtBwOqPLhpZB6GrNUkM3ZF52dMo6B6o'
    ranges = ["Лист1!A:F"]  #

    results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                       ranges=ranges,
                                                       valueRenderOption='UNFORMATTED_VALUE',
                                                       dateTimeRenderOption='FORMATTED_STRING').execute()
    sheet_values = results['valueRanges'][0]['values']
    with sq.connect('cars.db') as con:
        con.row_factory = sq.Row
        cursor = con.cursor()
        bd_sheets = []

        for rows in sheet_values[1:]:
            if len(rows) < 5:
                return 'не доконца заполнена/удалена информация в google sheets'

            car_make: str = (rows[0].strip())
            model: str = str(rows[1].strip())
            complete_set: str = rows[2].strip()

            if not check_correct_price(rows[3]) or not check_correct_price(rows[4]):
                return 'Поле Цена в google sheets заполнено неправильно'

            price: float = return_correct_prise(rows[3])
            price_turnkey: float = return_correct_prise(rows[4])
            photo_id: str = rows[5].strip()

            if any([not i for i in (car_make, model, price, complete_set, photo_id, price_turnkey)]):
                return 'Заполните все поля таблицы google sheets'
            bd_sheets.append((car_make, model, complete_set))
            cursor.execute(
                f'''
                SELECT count(*) as cnt, * FROM cars
                WHERE car_make={repr(car_make.strip())}
                AND model={repr(model.strip())}
                AND complete_set_of_the_machine={repr(complete_set.strip())}
                ''')

            for res in cursor:
                if res['cnt'] == 0:
                    cursor.execute(
                        f'''
                        INSERT INTO cars
                        (car_make, model, complete_set_of_the_machine, price, photo_id, price_turnkey)
                        VALUES
                        ({repr(car_make)}, {repr(model)}, {repr(complete_set)}, {repr(price)}, {repr(photo_id)}, {repr(price_turnkey)})
                        ''')
                else:
                    cursor.execute(
                        f'''
                        UPDATE cars
                        SET price = {repr(price)}, photo_id = {repr(photo_id)}, price_turnkey = {repr(price_turnkey)}
                        WHERE car_make={repr(car_make.strip())}
                        AND model={repr(model.strip())}
                        AND complete_set_of_the_machine={repr(complete_set.strip())}
                        ''')

        cursor.execute(
            f'''
            SELECT * FROM cars
            ''')

        lst_to_delete = []
        for res in cursor:
            if not (res['car_make'], res['model'], res['complete_set_of_the_machine']) in bd_sheets:
                lst_to_delete.append(
                    {'car_make': res['car_make'], 'model': res['model'], 'cs': res['complete_set_of_the_machine']})

        for elem in lst_to_delete:
            cursor.execute(
                f'''
                DELETE FROM cars
                WHERE car_make={repr(elem['car_make'].strip())}
                AND model={repr(elem['model'].strip())}
                AND complete_set_of_the_machine={repr(elem['cs'].strip())}
                '''
            )

    return 'Каталог успешно обновлён'


def return_correct_prise(price):
    if isinstance(price, str):
        price = float(price.replace(' ', '').replace(',', '.'))
        return price
    return float(price)


def check_correct_price(price):
    if isinstance(price, str):
        price = price.replace(' ', '').replace(',', '.')
        try:
            float(price)

        except ValueError:
            return False
    return True


if __name__ == '__main__':
    update_catalog()
