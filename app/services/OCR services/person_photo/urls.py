from django.urls import path
from person_photo.views import PersonPhotoView

urlpatterns = [
    path('person-photo/', PersonPhotoView.as_view(), name='person-photo-api'),
]
