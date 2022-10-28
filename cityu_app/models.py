from django.db import models
import os

# Create your models here.

class Png(models.Model):
    pngfile = models.FileField(upload_to='./CityU_POD')

    def filename(self):
        return os.path.basename(self.pngfile.name)

    def __str__(self):  # representation of object
        return str(self.pngfile)


class Excel(models.Model):
    excelfile = models.FileField()

    def filename(self):
        return os.path.basename(self.excelfile.name)

    def __str__(self):
        return str(self.excelfile)
