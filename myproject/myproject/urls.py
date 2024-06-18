from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponseRedirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reports/', include('reports.urls')),
    path('', lambda request: HttpResponseRedirect('/reports/')),  # Redirect the root URL to /reports/
]
