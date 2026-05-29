from celery import Celery
import json
from ollama import Client
from .config import settings
from .schemas import CharacterResponseSchema

celery_app = Celery("ai_tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

SYSTEM_PROMPT = """
You are an expert Dungeon Master for D&D 5e.
Your task: Analyze the user's character concept and return a STRICTLY valid JSON object.


ALLOWED CLASSES: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard.
ALLOWED RACES: Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling, Grung.
ALLOWED ALIGNMENTS: Lawful Good, Neutral Good, Chaotic Good, Lawful Neutral, True Neutral, Chaotic Neutral, Lawful Evil, Neutral Evil, Chaotic Evil.
ALLOWED BACKGROUND: Acolyte, Artisan, Charlatan, Criminal, Entertainer, Folk Hero, Hermit. Noble, Outlander, Sage, Sailor, Soldier, Urchin


RULES:
1. Return ONLY JSON. No markdown, no conversational text.
2. Technical fields (race, char_class, alignment, background) must be in ENGLISH and match the allowed lists.
3. The "backstory" and "name" fields must be in RUSSIAN.
4. "stat_priority" must be an array of 6 strings: "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma", sorted from most to least important.
5. If the concept is a famous character, stay true to their original nature.
6. If the user does not provide a name, generate a name that fits the setting and race. Do not use generic or stereotypical names.
7. The character name should be a proper name, not a title.
8. Write the backstory in the third person. Do not use "I", "me", or "my".
9. Write the backstory as a single string. Do not use multiple "backstory" keys. Use \n for line breaks within the "backstory" string if multiple paragraphs are needed.



RESPONSE FORMAT:
{
  "name": "Подходящее по расе имя на русском",
  "race": "Race in English",
  "char_class": "Class in English",
  "subclass": "Subclass in English or empty",
  "background": "Background in English",
  "alignment": "Alignment in English",
  "stat_priority": ["stat1", "stat2", "stat3", "stat4", "stat5", "stat6"],
  "backstory": "История персонажа на русском (3-4 предложения)."
}

USER CONSEPT: 
"""

@celery_app.task(name="tasks.generate_character_task")
def generate_character_task(user_concept: str) -> dict:
    try:
        client = Client(host=settings.OLLAMA_HOST)
        full_prompt = f"{SYSTEM_PROMPT}\nUSER CONCEPT: {user_concept}"
        
        response = client.generate(
            model=settings.OLLAMA_MODEL, 
            prompt=full_prompt, 
            format='json'
        )
        
        char_data = json.loads(response['response'])
        
        # Схема Pydantic сама выполнит всю математику CharacterBuilder!
        validated_character = CharacterResponseSchema(**char_data)
        
        # Возвращаем словарь — Celery сохранит его в Redis как результат выполнения задачи
        return validated_character.model_dump()
        
    except Exception as e:
        raise RuntimeError(f"Generation failed: {str(e)}")