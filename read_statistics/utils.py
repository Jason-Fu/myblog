import datetime
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, F, Value, Sum
from django.utils import timezone
from .models import ReadNumber,ReadNumberByDay

def read_statistics_once(request,obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" %(ct.model,obj.pk)
    if not request.COOKIES.get('blog_%s_read' % obj.pk):
        readnum,created = ReadNumber.objects.get_or_create(content_type=ct ,object_id=obj.pk)
        readnum.read_number = F('read_number') + 1
        readnum.save()

        readnumbyday, created = ReadNumberByDay.objects.get_or_create(content_type=ct, object_id=obj.pk,date=timezone.now().date())
        readnumbyday.read_number=F('read_number') + 1
        readnumbyday.save()
    return key

def get_7days_read_num(content_type):
    today = timezone.now().date()
    dates=[]
    read_num=[]
    for i in range(7,0,-1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m%d'))
        read_details = ReadNumberByDay.objects.filter(content_type=content_type,date=date)
        result = read_details.aggregate(sum=Sum('read_number'))
        read_num.append(result['sum'] or 0)
    return dates,read_num

