from django.db import models

class Observer(models.Model):
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    register_date=models.DateTimeField(null=True,blank=True,auto_now_add=True)
    

    def __str__(self):
        return self.name
