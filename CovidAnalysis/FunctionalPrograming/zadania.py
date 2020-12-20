from utils import *


def zad1():
    start_date = '2020-09-01'
    end_date = '2020-09-30'
    continent = 'South America'

    data = get_data(DATA_FILE_NAME, continent=continent)
    data = in_date_range(data, start_date, end_date)
    res = least_lethal_countries(data)

    return least_lethal_countries(data)


def zad2():
    data = get_data(DATA_FILE_NAME)
    return(most_new_cases_per_million(data))


def zad3():
    continent = 'South America'
    first_period = ['2020-04-01', '2020-04-30']
    second_period = ['2020-09-01', '2020-09-30']

    data = get_data(DATA_FILE_NAME, continent=continent)
    return(highest_daily_cases_increase(data, first_period, second_period))


def zad4():
    continent = 'South America'
    first_period = ['2020-04-01', '2020-04-30']
    second_period = ['2020-09-01', '2020-09-30']

    def annotate_avg_daily_cases(period):
        def categorize(avg):
            return 1 if avg < max_avg/3 else (2 if avg < max_avg/3*2 else 3)

        df = average_daily_cases(data, period)
        max_avg = df['avg_daily_cases'].max()
        df['category'] = df['avg_daily_cases'].apply(categorize)
        return df

    data = get_data(continent=continent)
    data_first = in_date_range(data, *first_period)
    data_second = in_date_range(data, *second_period)

    common_countries = set(data_first.groupby('location').groups.keys()
                           ) & set(data_second.groupby('location').groups.keys())

    data = data[data['location'].isin(common_countries)]
    categorized_first = annotate_avg_daily_cases(first_period)
    categorized_second = annotate_avg_daily_cases(second_period)

    result = [
        first[0] for first, second
        in zip(categorized_first.iterrows(), categorized_second.iterrows())
        if first[1][1] > second[1][1]
    ]
    return(result)


if __name__ == '__main__':
    print(zad1())
    print(zad2())
    print(zad3())
    print(zad4())
    pass
