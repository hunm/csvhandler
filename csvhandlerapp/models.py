from django.db import models


class File(models.Model):
    filename = models.FileField(upload_to='files')
    status = models.CharField(max_length=20, default='NEW')
    content = models.JSONField(null=True)


class Object(models.Model):
    id = models.IntegerField()
    uuid = models.CharField(max_length=40, unique=True)
    text = models.TextField()
    timestamp = models.DateTimeField()
