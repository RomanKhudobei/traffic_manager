"""traffic_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from manager import views as manager_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('source/statistic/<str:token>/', manager_views.source_statistic_view, name='source_statistic'),
    path('api/', include(('manager.api.urls', 'manager'), namespace='manager')),
]
