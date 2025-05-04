from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cms/', include('cms.urls')),
    path('', include('frontend.urls', namespace='frontend')),
    path('', include('guest_user.urls')),
]
