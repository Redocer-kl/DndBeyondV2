from django.urls import path
from .views import *

urlpatterns = [
    path('generate/', GenerateCharacterStartView.as_view(), name='start-generation'),
    path('generate/status/<int:task_id>/', CheckGenerationStatusView.as_view(), name='check-generation-status'),
]