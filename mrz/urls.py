from django.urls import path
from mrz.views import MRZView

urlpatterns = [
    path('mrz/', MRZView.as_view(), name='mrz-api'),
]
