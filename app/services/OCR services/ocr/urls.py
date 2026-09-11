from django.urls import path
from ocr.views import OCRView, DocumentPipelineView

urlpatterns = [
    path('ocr/', OCRView.as_view(), name='ocr-api'),
    path('process-document/', DocumentPipelineView.as_view(), name='process-document-pipeline'),
]
