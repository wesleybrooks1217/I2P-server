from django.db import models

# Create your models here.

class College(models.Model):
    name = models.CharField(max_length=120, blank=True, default="")
    acceptance_rate = models.FloatField(default=0.0, blank=True)
    sat_score = models.IntegerField(blank=True, default=0)
    average_fin_aid = models.IntegerField(blank=True, default=0)
    yearly_earnings = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return self.name

