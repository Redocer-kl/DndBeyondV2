import json
import logging
from character_creation.models import Character, Race, CharClass, AIConceptLog

logger = logging.getLogger(__name__)

class CharacterBuilder:
    STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]

    def __init__(self, user, ai_json_response, original_concept=""):
        self.user = user
        self.data = ai_json_response
        self.concept = original_concept

    def create_character(self):
        race_obj = Race.objects.filter(name__iexact=self.data.get('race')).first()
        class_obj = CharClass.objects.filter(name__iexact=self.data.get('char_class')).first()

        # 1. Распределяем базовые статы (Standard Array)
        stats = self._map_stats(self.data.get('stat_priority', []))

        # 2. Применяем расовые бонусы (ЕЩЕ ДО создания объекта Character)
        if race_obj:
            stats['strength'] += race_obj.str_bonus
            stats['dexterity'] += race_obj.dex_bonus
            stats['constitution'] += race_obj.con_bonus
            stats['intelligence'] += race_obj.int_bonus
            stats['wisdom'] += race_obj.wis_bonus
            stats['charisma'] += race_obj.cha_bonus

        # 3. Создаем объект
        character = Character(
            user=self.user,
            name=self.data.get('name', 'Безымянный герой'),
            concept_origin=self.concept,
            backstory=self.data.get('backstory', ''),
            race=race_obj.name if race_obj else self.data.get('race'),
            char_class=class_obj.name if class_obj else self.data.get('char_class'),
            subclass=self.data.get('subclass', ''),
            alignment=self.data.get('alignment', ''),
            background=self.data.get('background', ''),
            speed=race_obj.speed if race_obj else 30,
            size=race_obj.size if race_obj else "Medium",
            hit_die=class_obj.hit_die if class_obj else "1d8",
            features=race_obj.features,
            **stats
        )

        if class_obj:
            self._apply_saving_throws(character, class_obj.saving_throws)

        # Расчеты HP и AC уже учитывают модификаторы от итоговых (с бонусами) статов
        character.max_hp = self._calculate_start_hp(character)
        character.current_hp = character.max_hp
        character.armor_class = 10 + character.get_modifier(character.dexterity)

        character.save()
        return character

    def _map_stats(self, priority_list):
        """Маппит Standard Array [15, 14...] на статы по списку приоритетов"""
        stats = {
            "strength": 8, "dexterity": 8, "constitution": 8,
            "intelligence": 8, "wisdom": 8, "charisma": 8
        }
        
        # Если ИИ прислал некорректный список, используем порядок по умолчанию
        if not priority_list or len(priority_list) < 6:
            priority_list = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

        for i, stat_name in enumerate(priority_list):
            clean_name = stat_name.lower().strip()
            if clean_name in stats and i < len(self.STANDARD_ARRAY):
                stats[clean_name] = self.STANDARD_ARRAY[i]
        
        return stats

    def _apply_saving_throws(self, character, throws_str):
        """Устанавливает True для соответствующих полей prof_..._save"""
        throws = [t.strip().lower() for t in throws_str.split(',')]
        for throw in throws:
            field_name = f"prof_{throw[:3]}_save" # превращает strength в prof_str_save
            if hasattr(character, field_name):
                setattr(character, field_name, True)

    def _calculate_start_hp(self, character):
        """1 уровень: Max Hit Die + Con Modifier"""
        # Извлекаем число из '1d10' -> 10
        try:
            die_value = int(character.hit_die.lower().replace('1d', ''))
        except:
            die_value = 8
        return die_value + character.get_modifier(character.constitution)