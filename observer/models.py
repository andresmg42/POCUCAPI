from django.db import models

class Observer(models.Model):
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    telephone=models.IntegerField()

    def __str__(self):
        return self.name
