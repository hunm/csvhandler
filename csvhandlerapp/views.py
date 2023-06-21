from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from .models import File
from .serializers import FileSerializer
from .tasks import handle_csv
from rest_framework.parsers import MultiPartParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, inline_serializer
from django.core.exceptions import ObjectDoesNotExist


class UploadFileView(CreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = [MultiPartParser]

    @extend_schema(
        description="Upload file",
        responses={
            201: inline_serializer(
                name='Success file upload',
                fields={
                    'msg': serializers.CharField(default="File added to queue"),
                    'file_id': serializers.IntegerField(default=12),
                    'task_id': serializers.CharField()
                }
            ),
            415: inline_serializer(
                name='Wrong file extension',
                fields={
                    'msg': serializers.CharField(default="Wrong file extension")
                }
            )
        }
    )
    @csrf_exempt
    def post(self, request, *args, **kwargs):

        if request.FILES['filename'].name.split('.')[-1] == 'csv':
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            task = handle_csv.delay(serializer.data['id'])

            response = {
                'msg': "File added to queue",
                'file_id': f"{serializer.data['id']}",
                'task_id': task.id
            }
            return Response(response, 201)
        else:
            response = {
                'msg': "Wrong file extension"
            }
            return Response(response, 415)


class GetFileView(RetrieveAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    @extend_schema(
        description="Get file status",
        responses={
            200: inline_serializer(
                name='Success get status request',
                fields={
                    'file_id': serializers.IntegerField(default=12),
                    'status': serializers.CharField(default='FINISHED')
                }
            ),
            404: inline_serializer(
                name='File not found',
                fields={
                    'file_id': serializers.IntegerField(default=12),
                    'status': serializers.CharField(default='File not found')
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            file = self.queryset.get(id=kwargs['key_id'])
        except ObjectDoesNotExist:
            response = {
                'file_id': kwargs['key_id'],
                'status': 'File not found'
            }
            return Response(response, status=404)
        response = {
            'file_id': kwargs['key_id'],
            'status': file.status
        }
        return Response(response, status=200)


class FindInFileView(RetrieveAPIView):
    serializer_class = FileSerializer

    def get_queryset(self):
        return File.objects.get(text=self.kwargs['key_id'])

    @extend_schema(
        parameters=[
            OpenApiParameter(name='text', required=False, type=str),
            OpenApiParameter(name='uuid', required=False, type=str),
        ],
        description="Search in file",
        responses={
            102: inline_serializer(
                name='File yet in handling',
                fields={
                    'result': serializers.CharField(default='File handling in status PROCESSING')
                }
            ),
            200: inline_serializer(
                name='Success search',
                fields={
                        'result': serializers.JSONField(default=[
                                {
                                    "id": "6",
                                    "text": "text",
                                    "uuid": "e6455985-e428-4cdf-8623-8d4e37948d52",
                                    "timestamp": "12345"
                                }
                        ])
                    }
            ),
            404: inline_serializer(
                name='File not found',
                fields={
                    'result': serializers.CharField(default='File 7 not found')
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            file = self.get_queryset()
        except ObjectDoesNotExist:
            response = {
                'result': f'File {kwargs["key_id"]} not found'
            }
            return Response(response, status=404)
        result = []
        uuid, text = request.GET.get('uuid'), request.GET.get('text')
        if file.status == 'FINISHED':
            if uuid:
                for row in file.content:
                    if row['uuid'] == uuid:
                        result.append(row)
            elif text:
                for row in file.content:
                    if row['text'] == text:
                        result.append(row)

            response = {
                'result': sorted(result, key=lambda d: d['timestamp'])
            }

            return Response(response, status=200)
        else:
            response = {
                'result': f'File handling in status {file.status}'
            }
            return Response(response, status=102)
