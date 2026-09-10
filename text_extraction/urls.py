from django.urls import path
from text_extraction.views import TextExtractionView

urlpatterns = [
    path('extract/', TextExtractionView.as_view(), name='extract-api'),
]
