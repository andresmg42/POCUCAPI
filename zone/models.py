from django.db import models
from django.utils.translation import gettext_lazy as _
from campus.models import Campus

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

    campus=models.ForeignKey(Campus,on_delete=models.CASCADE,related_name='zones',null=True)
    
    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=['campus','number'],
                name='unique_number_by_campus_zone'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.get_zone_type_display()})'
