from django.db import models


class Continent(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta():
        ordering = ['name']

    def __str__(self):
        return self.name


class Country(models.Model):
    continent = models.ForeignKey(
        Continent, on_delete=models.CASCADE, related_name='countries')
    name = models.CharField(max_length=30, unique=True)

    class Meta():
        ordering = ['continent__name', 'name']

    def __str__(self):
        return self.name


class Entry(models.Model):
    date = models.DateField()
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name='entries')
    new_cases = models.IntegerField(null=True)
    new_cases_per_million = models.FloatField(null=True)
    new_deaths = models.IntegerField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['country', 'date',], name='unique date for country')
        ]
        ordering = ['country__continent__name', 'country__name', 'date']
