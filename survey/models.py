from django.db import models



class Survey(models.Model):
    name=models.CharField(max_length=50)
    topic=models.CharField(max_length=20)
    version=models.CharField(max_length=10)
    description=models.CharField(max_length=100)
    uploaded_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    image_url=models.CharField(max_length=100,null=True)
    

    def __str__(self):
        return self.name
