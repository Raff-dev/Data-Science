import requests
import json


def lab3():
    API_GET_RANKED_UP_URL = 'http://localhost:8000/Covid/get_ranked_up/'
    HEADERS = {'Content-type': 'application/json'}

    ranked_up_data_json = json.dumps({
        'continent_name': 'South America',
        'first_period': ['2020-04-01', '2020-04-30'],
        'second_period': ['2020-09-01', '2020-09-30']
    })
    res = requests.get(
        url=API_GET_RANKED_UP_URL,
        headers=HEADERS,
        data=ranked_up_data_json
    )
    print(res.json())


if __name__ == '__main__':
    lab3()
