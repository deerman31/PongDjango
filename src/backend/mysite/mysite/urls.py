from django.contrib import admin
#from django.conf import settings
#from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path("api/", include("accounts.urls")),
    path('admin/', admin.site.urls),
] 
# + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[1])