from django.db import models


class Option(models.Model):

    class InputType(models.TextChoices):
        NUMERIC = "NUM", "Numerico"
        TEXT = "STR", "Textual"

    description=models.CharField(max_length=30)
    type= models.CharField(max_length=3, choices=InputType.choices,default=InputType.NUMERIC )

    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=['description','type'],
                name='unique descripiton by input type'
            )
        ]
    def __str__(self):
        return self.description
