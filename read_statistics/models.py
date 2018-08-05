from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import exceptions
from django.utils import timezone

class ReadNumber(models.Model):
    read_number = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType,on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type','object_id')

class ReadNumExpand():
    def get_read_number(self):
        ct = ContentType.objects.get_for_model(self)
        try:
            readnum = ReadNumber.objects.get(content_type=ct,object_id=self.pk).read_number
        except exceptions.ObjectDoesNotExist:
            readnum = 0
        return readnum


class ReadNumberByDay(models.Model):
    date = models.DateField(default=timezone.now)
    read_number = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType,on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type','object_id')