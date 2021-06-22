from django.db import models

# Create your models here.

class WeatherForecastDay(models.Model):
    country_code = models.CharField(max_length=8)
    for_day = models.DateField()
    average_temp_c = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('country_code', 'for_day',)

    def __str__(self):
        return f'{self.country_code} {self.for_day}'