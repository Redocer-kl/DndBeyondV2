from django.core.management.base import BaseCommand
from character_creation.models import Race, CharClass

RACES = [
    {
        "name": "Human",
        "rus_name": "Человек",
        "speed": 30,
        "size": "Medium",
        "str_bonus": 1, "dex_bonus": 1, "con_bonus": 1, "int_bonus": 1, "wis_bonus": 1, "cha_bonus": 1,
        "features": "Универсальность, адаптивность, бонус к любым качествам по усмотрению мира."
    },
    {
        "name": "Elf",
        "rus_name": "Эльф",
        "speed": 30,
        "size": "Medium",
        "str_bonus": 0, "dex_bonus": 2, "con_bonus": 0, "int_bonus": 1, "wis_bonus": 0, "cha_bonus": 0,
        "features": "Тёмное зрение, острые чувства, эльфийская невосприимчивость к очарованию, медитация вместо сна."
    },
    {
        "name": "Dwarf",
        "rus_name": "Дварф",
        "speed": 25,
        "size": "Medium",
        "str_bonus": 0, "dex_bonus": 0, "con_bonus": 2, "int_bonus": 0, "wis_bonus": 1, "cha_bonus": 0,
        "features": "Тёмное зрение, стойкость к яду, мастерство камня и ремёсел."
    },
    {
        "name": "Halfling",
        "rus_name": "Полурослик",
        "speed": 25,
        "size": "Small",
        "str_bonus": 0, "dex_bonus": 2, "con_bonus": 0, "int_bonus": 0, "wis_bonus": 0, "cha_bonus": 1,
        "features": "Везучесть, храбрость, ловкость и умение проходить сквозь более крупных существ."
    },
    {
        "name": "Dragonborn",
        "rus_name": "Драконорождённый",
        "speed": 30,
        "size": "Medium",
        "str_bonus": 2, "dex_bonus": 0, "con_bonus": 0, "int_bonus": 0, "wis_bonus": 0, "cha_bonus": 1,
        "features": "Драконья дыхательная атака, сопротивление выбранному виду урона, драконье наследие."
    },
    {
        "name": "Gnome",
        "rus_name": "Гном",
        "speed": 25,
        "size": "Small",
        "str_bonus": 0, "dex_bonus": 0, "con_bonus": 1, "int_bonus": 2, "wis_bonus": 0, "cha_bonus": 0,
        "features": "Тёмное зрение, гномья хитрость, высокий интеллект и изобретательность."
    },
    {
        "name": "Half-Elf",
        "rus_name": "Полуэльф",
        "speed": 30,
        "size": "Medium",
        "str_bonus": 0, "dex_bonus": 1, "con_bonus": 0, "int_bonus": 1, "wis_bonus": 0, "cha_bonus": 2,
        "features": "Тёмное зрение, эльфийское наследие, гибкость и дополнительные навыки."
    },
    {
        "name": "Half-Orc",
        "rus_name": "Полуорк",
        "speed": 30,
        "size": "Medium",
        "str_bonus": 2, "dex_bonus": 0, "con_bonus": 1, "int_bonus": 0, "wis_bonus": 0, "cha_bonus": 0,
        "features": "Тёмное зрение, стойкость, ярость в бою и грубая сила."
    },
    {
        "name": "Tiefling",
        "rus_name": "Тифлинг",
        "speed": 30,
        "size": "Medium",
        "str_bonus": 0, "dex_bonus": 0, "con_bonus": 0, "int_bonus": 1, "wis_bonus": 0, "cha_bonus": 2,
        "features": "Тёмное зрение, сопротивление огню, инфернальное наследие и магические способности."
    },
    {
        "name": "Grung",
        "rus_name": "Грунг",
        "speed": 25,
        "size": "Small",
        "str_bonus": 0, "dex_bonus": 2, "con_bonus": 1, "int_bonus": 0, "wis_bonus": 0, "cha_bonus": 0,
        "features": "Амфибия, ядовитая кожа, высокий прыжок, зависимость от воды."
    },
]

CLASSES = [
    {"name": "Barbarian", "rus_name": "Варвар", "hit_die": "1d12", "saving_throws": "strength,constitution", "skill_slots": 2},
    {"name": "Bard", "rus_name": "Бард", "hit_die": "1d8", "saving_throws": "dexterity,charisma", "skill_slots": 3},
    {"name": "Cleric", "rus_name": "Жрец", "hit_die": "1d8", "saving_throws": "wisdom,charisma", "skill_slots": 2},
    {"name": "Druid", "rus_name": "Друид", "hit_die": "1d8", "saving_throws": "intelligence,wisdom", "skill_slots": 2},
    {"name": "Fighter", "rus_name": "Воин", "hit_die": "1d10", "saving_throws": "strength,constitution", "skill_slots": 2},
    {"name": "Monk", "rus_name": "Монах", "hit_die": "1d8", "saving_throws": "strength,dexterity", "skill_slots": 2},
    {"name": "Paladin", "rus_name": "Паладин", "hit_die": "1d10", "saving_throws": "wisdom,charisma", "skill_slots": 2},
    {"name": "Ranger", "rus_name": "Следопыт", "hit_die": "1d10", "saving_throws": "strength,dexterity", "skill_slots": 3},
    {"name": "Rogue", "rus_name": "Плут", "hit_die": "1d8", "saving_throws": "dexterity,intelligence", "skill_slots": 4},
    {"name": "Sorcerer", "rus_name": "Чародей", "hit_die": "1d6", "saving_throws": "constitution,charisma", "skill_slots": 2},
    {"name": "Warlock", "rus_name": "Колдун", "hit_die": "1d8", "saving_throws": "wisdom,charisma", "skill_slots": 2},
    {"name": "Wizard", "rus_name": "Волшебник", "hit_die": "1d6", "saving_throws": "intelligence,wisdom", "skill_slots": 2},
]


class Command(BaseCommand):
    help = "Заполняет справочники Race и CharClass"

    def handle(self, *args, **options):
        race_updated = 0
        class_updated = 0

        for item in RACES:

            obj, created = Race.objects.update_or_create(
                name=item["name"],
                defaults={
                    "rus_name": item["rus_name"],
                    "speed": item["speed"],
                    "size": item["size"],
                    "str_bonus": item["str_bonus"],
                    "dex_bonus": item["dex_bonus"],
                    "con_bonus": item["con_bonus"],
                    "int_bonus": item["int_bonus"],
                    "wis_bonus": item["wis_bonus"],
                    "cha_bonus": item["cha_bonus"],
                    "features": item["features"],
                },
            )
            race_updated += 1

        for item in CLASSES:
            obj, created = CharClass.objects.update_or_create(
                name=item["name"],
                defaults={
                    "rus_name": item["rus_name"],
                    "hit_die": item["hit_die"],
                    "saving_throws": item["saving_throws"],
                    "skill_slots": item["skill_slots"],
                },
            )
            class_updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"База обновлена! Обработано рас: {race_updated}, классов: {class_updated}"
        ))