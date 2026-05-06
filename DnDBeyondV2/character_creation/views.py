from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AIConceptLog
from .services.ai_character import CharacterBuilder
from .serializers import CharacterDetailSerializer
import json
import ollama 
from django.shortcuts import get_object_or_404
from .tasks import generate_character_task


class GenerateCharacterStartView(APIView):
    """
    Эндпоинт 1: Принимает концепт, создает задачу, отдает ID задачи.
    Работает за < 100мс.
    """
    def post(self, request):
        user_concept = request.data.get('concept')
        if not user_concept:
            return Response({"error": "Concept is required"}, status=400)
        
        log = AIConceptLog.objects.create(
            user=request.user,
            concept=user_concept,
            status='pending'
        )

        generate_character_task.delay(log.id, request.user.id, user_concept)

        return Response({
            "task_id": log.id,
            "status": "pending",
            "message": "Генерация запущена. Пожалуйста, подождите."
        }, status=202) # 202 Accepted


class CheckGenerationStatusView(APIView):
    """
    Эндпоинт 2: Фронтенд опрашивает его раз в пару секунд.
    """
    def get(self, request, task_id):
        log = get_object_or_404(AIConceptLog, id=task_id, user=request.user)

        if log.status == 'pending':
            return Response({"status": "pending"})
            
        elif log.status == 'error':
            return Response({
                "status": "error", 
                "error": log.error_message
            }, status=400)
            
        elif log.status == 'success':
            # Нейронка закончила, отдаем готового персонажа!
            serializer = CharacterDetailSerializer(log.character)
            return Response({
                "status": "success",
                "character": serializer.data
            })