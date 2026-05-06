from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def character_directory_path(instance, filename):
    return f'user_{instance.user.id}/chars/{filename}'

from django.db import models
from django.contrib.auth import get_user_model
import math

User = get_user_model()

def character_directory_path(instance, filename):
    return f'user_{instance.user.id}/chars/{filename}'

class Character(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField("Имя персонажа", max_length=100)
    avatar = models.ImageField(upload_to=character_directory_path, null=True, blank=True)
    
    # Системные поля
    is_draft = models.BooleanField("Черновик", default=True)
    experience_points = models.PositiveIntegerField("Опыт", default=0)
    
    # Основные параметры
    race = models.CharField("Раса", max_length=50)
    char_class = models.CharField("Класс", max_length=50)
    subclass = models.CharField("Подкласс", max_length=50, blank=True)
    level = models.PositiveIntegerField(default=1)
    
    # Характеристики
    strength = models.IntegerField(default=8)
    dexterity = models.IntegerField(default=8)
    constitution = models.IntegerField(default=8)
    intelligence = models.IntegerField(default=8)
    wisdom = models.IntegerField(default=8)
    charisma = models.IntegerField(default=8)

    armor_class = models.PositiveIntegerField("Класс доспеха", default=10)
    speed = models.PositiveIntegerField("Скорость", default=30)
    initiative = models.IntegerField("Инициатива", default=0)
    max_hp = models.PositiveIntegerField("Макс. ХП", default=10)
    current_hp = models.IntegerField("Текущие ХП", default=10)
    hit_die = models.CharField("Кость хитов", max_length=10, default="1d8")
    alignment = models.CharField("Мировоззрение", max_length=50, blank=True)
    size = models.CharField("Размер", max_length=20, default="Medium")

    # Навыки (Владение)
    prof_athletics = models.BooleanField(default=False)
    prof_acrobatics = models.BooleanField(default=False)
    prof_sleight_of_hand = models.BooleanField(default=False)
    prof_stealth = models.BooleanField(default=False)
    prof_arcana = models.BooleanField(default=False)
    prof_history = models.BooleanField(default=False)
    prof_investigation = models.BooleanField(default=False)
    prof_nature = models.BooleanField(default=False)
    prof_religion = models.BooleanField(default=False)
    prof_animal_handling = models.BooleanField(default=False)
    prof_insight = models.BooleanField(default=False)
    prof_medicine = models.BooleanField(default=False)
    prof_perception = models.BooleanField(default=False)
    prof_survival = models.BooleanField(default=False)
    prof_deception = models.BooleanField(default=False)
    prof_intimidation = models.BooleanField(default=False)
    prof_performance = models.BooleanField(default=False)
    prof_persuasion = models.BooleanField(default=False)

    # Спасброски
    prof_str_save = models.BooleanField(default=False)
    prof_dex_save = models.BooleanField(default=False)
    prof_con_save = models.BooleanField(default=False)
    prof_int_save = models.BooleanField(default=False)
    prof_wis_save = models.BooleanField(default=False)
    prof_cha_save = models.BooleanField(default=False)

    background = models.CharField("Предыстория", max_length=100, blank=True)
    features = models.TextField("Умения и особенности", blank=True)
    
    # Поля для инвентаря и магии
    equipment = models.TextField("Снаряжение", blank=True)
    languages = models.TextField("Языки", blank=True)
    tool_proficiencies = models.TextField("Инструменты", blank=True)
    gold = models.PositiveIntegerField("Золото", default=0)
    spells = models.JSONField("Список заклинаний", default=list, blank=True)

    concept_origin = models.TextField("Исходный концепт", blank=True)
    backstory = models.TextField("Предыстория", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def proficiency_bonus(self):
        return math.ceil(self.level / 4) + 1

    def get_modifier(self, ability_score):
        return (ability_score - 10) // 2

    def __str__(self):
        return f"{self.name} ({self.char_class} {self.level})"

class AIConceptLog(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('success', 'Успешно'),
        ('error', 'Ошибка'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    concept = models.TextField() # То, что ввел юзер
    prompt = models.TextField(blank=True, null=True)
    ai_response = models.JSONField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    character = models.ForeignKey('Character', on_delete=models.SET_NULL, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

class Race(models.Model):
    name = models.CharField(max_length=50, unique=True)
    rus_name = models.CharField(max_length=50, unique=True)
    speed = models.PositiveIntegerField(default=30)
    size = models.CharField(max_length=20, default="Medium")
    
    # Бонусы к характеристикам
    str_bonus = models.IntegerField(default=0)
    dex_bonus = models.IntegerField(default=0)
    con_bonus = models.IntegerField(default=0)
    int_bonus = models.IntegerField(default=0)
    wis_bonus = models.IntegerField(default=0)
    cha_bonus = models.IntegerField(default=0)
    
    features = models.TextField(help_text="Расовые особенности")

    def __str__(self):
        return self.name

class CharClass(models.Model):
    name = models.CharField(max_length=50, unique=True)
    rus_name = models.CharField(max_length=50, unique=True)
    hit_die = models.CharField(max_length=5, default="1d8")
    # Спасброски храним строкой через запятую, например: "strength,constitution"
    saving_throws = models.CharField(max_length=100)
    skill_slots = models.PositiveIntegerField(default=2)

    def __str__(self):
        return self.name