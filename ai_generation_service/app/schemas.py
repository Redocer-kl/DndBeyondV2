from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict
from .data_maps import RACES_MAP, CLASSES_MAP

class CharacterGenerationRequest(BaseModel):
    concept: str = Field(..., example="Скрытный плут хафлинг, который вырос на улицах большого города.")

class CharacterResponseSchema(BaseModel):
    name: str
    race: str
    char_class: str
    subclass: Optional[str] = ""
    background: Optional[str] = ""
    alignment: Optional[str] = ""
    
    # Характеристики
    strength: int = 8
    dexterity: int = 8
    constitution: int = 8
    intelligence: int = 8
    wisdom: int = 8
    charisma: int = 8

    # Производные параметры
    level: int = 1
    armor_class: int = 10
    speed: int = 30
    size: str = "Medium"
    max_hp: int = 10
    current_hp: int = 10
    hit_die: str = "1d8"
    features: str = ""
    
    # Спасброски
    prof_str_save: bool = False
    prof_dex_save: bool = False
    prof_con_save: bool = False
    prof_int_save: bool = False
    prof_wis_save: bool = False
    prof_cha_save: bool = False

    proficiency_bonus: int = 2
    modifiers: Dict[str, int] = {}
    backstory: str

    @model_validator(mode="before")
    @classmethod
    def build_character_logic(cls, data: dict) -> dict:
        """
        Полный перенос логики из старого CharacterBuilder.
        """
        # Справочники
        race_name = str(data.get('race')).lower().strip()
        class_name = str(data.get('char_class')).lower().strip()
        
        race_obj = RACES_MAP.get(race_name)
        class_obj = CLASSES_MAP.get(class_name)

        # 1. Распределяем базовые статы (Standard Array) по приоритетам от ИИ
        standard_array = [15, 14, 13, 12, 10, 8]
        priority_list = data.get('stat_priority', [])
        if not priority_list or len(priority_list) < 6:
            priority_list = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

        stats = {s: 8 for s in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]}
        for i, stat_name in enumerate(priority_list):
            clean_name = stat_name.lower().strip()
            if clean_name in stats and i < len(standard_array):
                stats[clean_name] = standard_array[i]

        # 2. Применяем расовые бонусы
        if race_obj:
            bonuses = race_obj["bonuses"]
            for stat in stats:
                short_stat = stat[:3]  # превращаем strength -> str
                stats[stat] += bonuses.get(short_stat, 0)
        
        # Записываем статы обратно в data
        data.update(stats)

        # 3. Заполняем расовые и классовые параметры
        data["speed"] = race_obj["speed"] if race_obj else 30
        data["size"] = race_obj["size"] if race_obj else "Medium"
        data["features"] = race_obj["features"] if race_obj else ""
        data["hit_die"] = class_obj["hit_die"] if class_obj else "1d8"

        # 4. Спасброски
        if class_obj:
            for throw in class_obj["saving_throws"]:
                data[f"prof_{throw}_save"] = True

        # Вспомогательная функция модификатора
        def get_mod(score): return (score - 10) // 2

        # 5. Считаем модификаторы
        data["modifiers"] = {
            "str": get_mod(data["strength"]),
            "dex": get_mod(data["dexterity"]),
            "con": get_mod(data["constitution"]),
            "int": get_mod(data["intelligence"]),
            "wis": get_mod(data["wisdom"]),
            "cha": get_mod(data["charisma"]),
        }

        # 6. Расчет HP и AC
        try:
            die_value = int(data["hit_die"].lower().replace('1d', ''))
        except:
            die_value = 8
            
        data["max_hp"] = die_value + data["modifiers"]["con"]
        data["current_hp"] = data["max_hp"]
        data["armor_class"] = 10 + data["modifiers"]["dex"]
        data["proficiency_bonus"] = 2  # На 1 уровне всегда 2

        return data