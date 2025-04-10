from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cms/', include('cms.urls')),
    path('api/auth/', include('authapi.urls')),
    path('api/learn/', include('learnapi.urls')),
]
