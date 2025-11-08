import requests
import pandas as pd

if __name__ == '__main__':
    num = int(input('Введите целое число от 1 до 610 включительно: '))
    r = requests.post('http://localhost:5000/recommendations', json={'num':num})
    print(r.status_code)
    if r.status_code == 200:
        print('Recommendations:')
        response_dict = r.json()['recommendation']
        response_df = pd.DataFrame(response_dict)
        print(response_df)
    else:
        print(r.text)