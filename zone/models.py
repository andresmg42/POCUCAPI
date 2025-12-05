from django.db import models
from django.utils.translation import gettext_lazy as _

class Zone(models.Model):

    class ZoneType(models.TextChoices):
        OPEN='OP','Espacio Abierto'
        CLOSED='CL','Espacio Cerrado'
        MIXED='MX','Mixto (Abierto y Cerrado)'

    name=models.CharField(max_length=300)
    number=models.IntegerField(default=1)
    zone_type=models.CharField(
        max_length=2,
        choices=ZoneType.choices,
        default=ZoneType.MIXED
    )

    def __str__(self):
        return f'{self.name} ({self.get_zone_type_display()})'
