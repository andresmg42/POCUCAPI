from django.db import models
from zone.models import Zone

class Category(models.Model):
    name=models.CharField(max_length=100)
    image=models.CharField(max_length=200,null=True)
    target_zone_type = models.CharField(
        max_length=2,
        choices=Zone.ZoneType.choices,
        null=True, 
        blank=True,
        help_text="Dejar vacío si aplica para cualquier tipo de zona"
    )
    def __str__(self):
        return self.name
    

