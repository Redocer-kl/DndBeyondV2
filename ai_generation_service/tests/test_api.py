import pytest
from unittest.mock import patch, MagicMock
from app.schemas import CharacterResponseSchema


MOCK_OLLAMA_JSON = {
    "name": "Алёшка",
    "race": "Halfling",
    "char_class": "Rogue",
    "subclass": "Thief",
    "background": "Urchin",
    "alignment": "Chaotic Good",
    "stat_priority": ["dexterity", "constitution", "strength", "intelligence", "wisdom", "charisma"],
    "backstory": "Вырос на улицах шумного города..."
}

def test_character_schema_math():
    """
    Тест 1: Проверяем чистую математику внутри Pydantic схемы (CharacterResponseSchema).
    Проверяем, что Standard Array и расовые бонусы применяются корректно.
    """
    # Передаем сырые данные, имитируя ответ ИИ
    character = CharacterResponseSchema(**MOCK_OLLAMA_JSON)
    
    # Проверки:
    # Приоритет 1: Ловкость (Dex). Базовое 15 + 2 (раса Halfling) = 17. Модификатор +3
    assert character.dexterity == 17
    assert character.modifiers["dex"] == 3
    
    # Приоритет 2: Выносливость (Con). Базовое 14. Бонусов расы нет. Модификатор +2
    assert character.constitution == 14
    assert character.modifiers["con"] == 2
    
    # Приоритет 6: Харизма (Cha). Самый низкий приоритет из Standard Array = 8. Модификатор -1
    assert character.charisma == 8
    assert character.modifiers["cha"] == -1

    # Хиты: Плут (1d8 -> 8 базовых) + Мод Выносливости (+2) = 10
    assert character.max_hp == 10
    assert character.current_hp == 10

    # Класс Доспеха: 10 + Мод Ловкости (+3) = 13
    assert character.armor_class == 13

    # Спасброски Rogue: Ловкость и Интеллект
    assert character.prof_dex_save is True
    assert character.prof_int_save is True
    assert character.prof_str_save is False


@patch("app.tasks.Client")  # Мокаем класс Client из библиотеки ollama в файле app/tasks.py
def test_celery_task_integration(mock_ollama_client_class):
    """
    Тест 2: Проверяем Celery-таску в связке с моком Олламы.
    """
    # Настраиваем мок так, чтобы вызов client.generate(...) возвращал структуру Олламы
    mock_client_instance = MagicMock()
    mock_ollama_client_class.return_value = mock_client_instance
    
    import json
    mock_client_instance.generate.return_value = {
        "response": json.dumps(MOCK_OLLAMA_JSON)
    }

    # Импортируем таску и запускаем ее
    from app.tasks import generate_character_task
    
    result = generate_character_task("Хочу скрытного полурослика")
    
    # Проверяем, что таска успешно отработала, вызвала Олламу и вернула готовый валидный словарь
    assert result["name"] == "Алёшка"
    assert result["max_hp"] == 10
    assert mock_client_instance.generate.called is True


@patch("app.tasks.Client")
def test_fastapi_endpoints(mock_ollama_client_class, client):
    """
    Тест 3: Полный цикл через эндпоинты FastAPI.
    Поскольку в conftest включен task_always_eager=True, таска выполнится мгновенно
    прямо внутри POST-запроса, и результат сразу запишется в фейковый бэкенд Celery.
    """
    # Также настраиваем мок Олламы
    mock_client_instance = MagicMock()
    mock_ollama_client_class.return_value = mock_client_instance
    import json
    mock_client_instance.generate.return_value = {
        "response": json.dumps(MOCK_OLLAMA_JSON)
    }

    # 1. Делаем запрос на запуск генерации
    response = client.post("/api/v1/generate", json={"concept": "Скрытный вор"})
    assert response.status_code == 202
    
    data = response.json()
    assert "task_id" in data
    task_id = data["task_id"]

    # 2. Проверяем статус таски по полученному task_id
    status_response = client.get(f"/api/v1/status/{task_id}")
    assert status_response.status_code == 200
    
    status_data = status_response.json()
    assert status_data["status"] == "success"
    assert status_data["character"]["name"] == "Алёшка"
    assert status_data["character"]["armor_class"] == 13