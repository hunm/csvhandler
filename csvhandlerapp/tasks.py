from celery import shared_task
from .models import File
import csv


@shared_task
def handle_csv(file_id):
    jsonArray = []

    fileobj = File.objects.get(id=file_id)
    fileobj.status = 'PROCESSING'
    fileobj.save()

    try:
        with open(fileobj.filename.path, encoding='utf-8') as csvf:
            csvReader = csv.DictReader(csvf)
            for row in csvReader:
                jsonArray.append(row)

        fileobj.status = 'FINISHED'
        fileobj.content = jsonArray
        fileobj.save()

    except Exception as e:
        fileobj.status = 'ERROR'
        fileobj.content = e
        fileobj.save()

    return True
