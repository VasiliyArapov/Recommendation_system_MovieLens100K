import requests
import pandas as pd

if __name__ == '__main__':
    while True:
        try:
            num = int(input('Введите целое число от 1 до 610 включительно: '))
            if (num >= 1) and (num <= 610):
                r = requests.post('http://localhost:80/recommendations', json={'user_id':num})
                print(r.status_code)
                if r.status_code == 200:
                    print('Recommendations:')
                    response_dict = r.json()['recommendation']
                    response_df = pd.DataFrame(response_dict)
                    print(response_df)
                else:
                    print(r.text)
            else:
                print('Введен неверный id пользователя.')
        except Exception as e:
            print('Неверный ввод.')