from django.urls import path

from .views import GetRandomTargetsApiView


urlpatterns = [
    path('random-targets/', GetRandomTargetsApiView.as_view()),
]
