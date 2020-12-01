import pandas as pd
import datetime
from typing import List, Dict
import functools
import operator


DATA_FILE_NAME = 'covid_data.csv'


def get_data(file_name: str = DATA_FILE_NAME, continent: str = None) -> pd.DataFrame:
    """returns dataframe of cvs file data, filters by continent if specified"""
    df = pd.read_csv(file_name, error_bad_lines=False)
    return df[df['continent'] == continent] if continent else df


def in_date_range(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """ 
    date format -> string : 'yyyy-mm-dd'
    returns dataframe sorted by date, contained within data range.
    """
    df = df.sort_values(by='date', ascending=True)
    df = df[df['date'] >= start]
    df = df[df['date'] <= end]
    return df


def least_lethal_countries(df: pd.DataFrame, limit=10) -> List[str]:
    """retirns list of countries with the least deaths"""
    grouped = df.groupby('location').sum()
    sorted_by_lethality = grouped.sort_values(by='new_deaths', ascending=True)
    least_lethal_countries = list(sorted_by_lethality.index[:limit])
    return least_lethal_countries


def most_new_cases_per_million(df: pd.DataFrame) -> Dict[str, str]:
    """
    returns dictionary -> {continent : location} for each continent within dataframe,
    where location is the location with most new cases per million.
    """
    def first_from_continent(df, continent):
        return df[df['continent'] == continent].iloc[0].loc['location']

    continent_list = list(df['continent'].dropna().unique())
    df = df.sort_values('new_cases_per_million', ascending=False)

    return {
        continent: first_from_continent(df, continent)
        for continent in continent_list
    }


def get_days_count(start: str, end: str) -> int:
    """
    date format -> string :'yyyy-mm-dd'
    Calculates inclusive number of days given start and end dates
    """
    def to_date(s): return datetime.date(* [int(d) for d in s.split('-')])

    delta = to_date(end) - to_date(start)
    return delta.days + 1


def average_daily_cases(df: pd.DataFrame, period: List[str]) -> pd.DataFrame:
    """
    period -> [start,end]
    date format -> string :'yyyy-mm-dd'
    returns average daily cases for each location within given period
    """

    days_count = get_days_count(*period)
    period_data = in_date_range(df, *period)
    grouped_data = period_data.groupby('location').sum()

    grouped_data['avg_daily_cases'] = grouped_data['new_cases'].div(days_count)
    return grouped_data[['avg_daily_cases']]


def highest_daily_cases_increase(df: pd.DataFrame, first_period: List[str], second_period: List[str], limit=5):
    """
    period -> [start,end]
    date format -> string :'yyyy-mm-dd'
    """
    first_average_increase = average_daily_cases(df, first_period)[
        'avg_daily_cases']
    second_average_increase = average_daily_cases(df, second_period)[
        'avg_daily_cases']

    difference = second_average_increase - first_average_increase
    sorted_data = difference.sort_values(ascending=False)
    top_countries = list(sorted_data.iloc[:limit].index)
    return top_countries
