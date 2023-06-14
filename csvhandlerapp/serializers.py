from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = File
        fields = ('id', 'filename')
