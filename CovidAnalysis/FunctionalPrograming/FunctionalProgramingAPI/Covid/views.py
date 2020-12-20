import time
from django.core import serializers
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework import status
from django.db.models import Avg, F, Q, Exists, OuterRef

from .models import Continent, Country, Entry
import datetime


def string_to_datetime(string):
    return datetime.date(*[int(s) for s in string.split('-')])


class Covid(ViewSet):

    @action(methods=['post'], detail=False)
    def update_data(self, request, *args, **kwargs):
        try:
            data = request.data['data']
            for continent_data in data:
                name = continent_data['continent_name']
                continent, _ = Continent.objects.get_or_create(name=name)

                for country_data in continent_data['countries']:
                    name = country_data['country_name']
                    country, _ = Country.objects.get_or_create(
                        name=name, continent=continent)

                    for entry_data in country_data['entries']:
                        date = entry_data.pop('date')
                        date = string_to_datetime(date)
                        entry, _ = Entry.objects.get_or_create(
                            date=date, country=country)
                        Entry.objects.filter(id=entry.id).update(**entry_data)

            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f'Exception {e}')
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def get_ranked_up(self, request, *args, **kwargs):
        continent_names = request.data['continent_names']
        first_period = request.data['first_period']
        second_period = request.data['second_period']

        continent_countries = Country.objects.filter(
            Exists(Entry.objects.filter(
                country__id=OuterRef('id'), date__range=first_period)),
            Exists(Entry.objects.filter(
                country__id=OuterRef('id'), date__range=second_period)),
            continent__name__in=continent_names)

        def categorize(avg, max_avg):
            return 1 if avg < max_avg/3 else (2 if avg < max_avg/3*2 else 3)

        def annotate_countries(period):
            countries = continent_countries.filter(entries__date__range=period).annotate(
                avg_new_cases=Avg('entries__new_cases'))
            max_avg_new_cases = countries.latest('avg_new_cases').avg_new_cases
            print(max_avg_new_cases)
            return countries, max_avg_new_cases

        first_countries, first_max = annotate_countries(first_period)
        second_countries, second_max = annotate_countries(second_period)

        result = [
            {
                'first_max_avg_cases': first_max,
                'second_max_avg_cases': second_max,
                'countries': [{
                    'name': first.name,
                    'category': [categorize(first.avg_new_cases, first_max), categorize(second.avg_new_cases, second_max)],
                    'avg':[first.avg_new_cases, second.avg_new_cases],

                } for first, second
                    in zip(first_countries, second_countries)
                    if categorize(first.avg_new_cases, first_max) > categorize(second.avg_new_cases, second_max)]
            }
        ]

        return Response(data=result, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_entries(self, request, *args, **kwargs):
        continents = Continent.objects.all()

        if 'continent_names' in request.data.keys():
            continent_names = request.data['continent_names']
            continents = continents.filter(name__in=continent_names)

        if 'country_names' in request.data.keys():
            country_names = request.data['country_names']
            continents = continents.filter(countries__name__in=country_names)

        if 'period' in request.data.keys():
            period = request.data['period']
            continents = continents.filter(
                countries__entries__date__range=period)

        start = time.time()
        result = [{
            'continent': continent.name,
            'countries': [{
                'country': country.name,
                'entries': [
                    {
                        'date': entry.date,
                        'new_cases': entry.new_cases,
                        'new_cases_per_million': entry.new_cases_per_million,
                        'new_deaths': entry.new_deaths,
                    } for entry in country.entries.all()]
            } for country in continent.countries.all()]
        } for continent in continents]

        return Response(data=result, status=status.HTTP_200_OK)
