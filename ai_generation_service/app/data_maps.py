# Словари для симуляции того, что раньше лежало в моделях Race и CharClass

RACES_MAP = {
    "human": {"speed": 30, "size": "Medium", "features": "Каждый ваш параметр увеличивается на 1.", "bonuses": {"str": 1, "dex": 1, "con": 1, "int": 1, "wis": 1, "cha": 1}},
    "elf": {"speed": 30, "size": "Medium", "features": "Темное зрение, Острые чувства, Наследие фей.", "bonuses": {"str": 0, "dex": 2, "con": 0, "int": 0, "wis": 0, "cha": 0}},
    "dwarf": {"speed": 25, "size": "Medium", "features": "Темное зрение, Дварфская устойчивость, Знание камня.", "bonuses": {"str": 0, "dex": 0, "con": 2, "int": 0, "wis": 0, "cha": 0}},
    "halfling": {"speed": 25, "size": "Small", "features": "Удача, Храбрость, Проворство полуросликов.", "bonuses": {"str": 0, "dex": 2, "con": 0, "int": 0, "wis": 0, "cha": 0}},
    "dragonborn": {"speed": 30, "size": "Medium", "features": "Драконье наследие, Оружие дыхания.", "bonuses": {"str": 2, "dex": 0, "con": 0, "int": 0, "wis": 0, "cha": 1}},
    "gnome": {"speed": 25, "size": "Small", "features": "Темное зрение, Гномья хитрость.", "bonuses": {"str": 0, "dex": 0, "con": 0, "int": 2, "wis": 0, "cha": 0}},
    "half-elf": {"speed": 30, "size": "Medium", "features": "Темное зрение, Дипломатический такт.", "bonuses": {"str": 0, "dex": 0, "con": 0, "int": 0, "wis": 0, "cha": 2}},
    "half-orc": {"speed": 30, "size": "Medium", "features": "Темное зрение, Непоколебимая стойкость, Яростные атаки.", "bonuses": {"str": 2, "dex": 0, "con": 1, "int": 0, "wis": 0, "cha": 0}},
    "tiefling": {"speed": 30, "size": "Medium", "features": "Темное зрение, Адское сопротивление.", "bonuses": {"str": 0, "dex": 0, "con": 0, "int": 1, "wis": 0, "cha": 2}},
    "grung": {"speed": 25, "size": "Small", "features": "Амфибия, Ядовитая кожа, Прыжок в высоту.", "bonuses": {"str": 0, "dex": 2, "con": 1, "int": 0, "wis": 0, "cha": 0}},
}

CLASSES_MAP = {
    "barbarian": {"hit_die": "1d12", "saving_throws": ["str", "con"]},
    "bard": {"hit_die": "1d8", "saving_throws": ["dex", "cha"]},
    "cleric": {"hit_die": "1d8", "saving_throws": ["wis", "cha"]},
    "druid": {"hit_die": "1d8", "saving_throws": ["int", "wis"]},
    "fighter": {"hit_die": "1d10", "saving_throws": ["str", "con"]},
    "monk": {"hit_die": "1d8", "saving_throws": ["str", "dex"]},
    "paladin": {"hit_die": "1d10", "saving_throws": ["wis", "cha"]}, 
    "ranger": {"hit_die": "1d10", "saving_throws": ["str", "dex"]},
    "rogue": {"hit_die": "1d8", "saving_throws": ["dex", "int"]},
    "sorcerer": {"hit_die": "1d8", "saving_throws": ["con", "cha"]},
    "warlock": {"hit_die": "1d8", "saving_throws": ["wis", "cha"]},
    "wizard": {"hit_die": "1d6", "saving_throws": ["int", "wis"]},
}