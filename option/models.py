from django.db import models


class Option(models.Model):
    description=models.CharField(max_length=30)
    def __str__(self):
        return self.description
    



    

