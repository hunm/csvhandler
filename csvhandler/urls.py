from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from csvhandlerapp.views import UploadFileView, GetFileView, FindInFileView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/file/', UploadFileView.as_view()),
    path('api/file/get/<int:key_id>/', GetFileView.as_view()),
    path('api/file/find/<int:key_id>', FindInFileView.as_view()),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
