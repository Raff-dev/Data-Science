import numpy as np
import pandas as pd
import requests
import json

from utils import get_data


def get_post_data():

    def validate(data_type, value):
        return None if np.isnan(value) else data_type(value)

    data = get_data()
    post_data = {
        'data': [
            {
                'continent_name': continent_data['continent'].iloc[0],
                'countries':[
                    {
                        'country_name': country_data['location'].iloc[0],
                        'entries':[{
                            'date': entry_data['date'],
                            'new_cases':validate(int, entry_data['new_cases']),
                            'new_cases_per_million':validate(float, entry_data['new_cases_per_million']),
                            'new_deaths':validate(int, entry_data['new_deaths'])
                        } for _, entry_data in country_data.iterrows()]
                    } for country_data in [country_data for _, country_data in continent_data.groupby('location')]]
            }
            for continent_data in [continent_data for _, continent_data in data.groupby('continent')]
        ]
    }


def update(post_data):
    API_UPDATE_URL = 'http://localhost:8000/Covid/update_data/'
    HEADERS = {'Content-type': 'application/json'}
    json_post_data = json.dumps(post_data)

    requests.post(
        url=API_UPDATE_URL,
        headers=HEADERS,
        data=json_post_data
    )


if __name__ == '__main__':
    post_data = get_post_data()
    update(post_data)
