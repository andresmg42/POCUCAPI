from django.db import models

class Zone(models.Model):
    name=models.CharField(max_length=300)
    number=models.IntegerField(default=1)

    def __str__(self):
        return self.name
