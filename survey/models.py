from django.db import models

class Survey(models.Model):
    name=models.CharField(max_length=50)
    topic=models.CharField(max_length=20)
    version=models.CharField(max_length=10)
    description=models.CharField(max_length=100)

    def __str__(self):
        return self.name
