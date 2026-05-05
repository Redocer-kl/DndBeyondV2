from django.contrib import admin
from .models import Character, AIConceptLog, Race, CharClass


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "user", "race", "char_class", "level",
        "is_draft", "armor_class", "current_hp", "max_hp", "gold",
        "updated_at",
    )
    list_filter = ("is_draft", "race", "char_class", "level", "size", "created_at")
    search_fields = ("name", "user__username", "user__email", "race", "char_class", "background")
    readonly_fields = ("created_at", "updated_at", "proficiency_bonus_display")
    raw_id_fields = ("user",)
    ordering = ("-updated_at",)

    fieldsets = (
        ("Основное", {
            "fields": ("user", "name", "avatar", "is_draft", "experience_points")
        }),
        ("Базовые параметры", {
            "fields": ("race", "char_class", "subclass", "level", "background", "alignment", "size")
        }),
        ("Характеристики", {
            "fields": (
                "strength", "dexterity", "constitution",
                "intelligence", "wisdom", "charisma",
                "armor_class", "speed", "initiative",
                "max_hp", "current_hp", "hit_die",
            )
        }),
        ("Навыки", {
            "classes": ("collapse",),
            "fields": (
                "prof_athletics", "prof_acrobatics", "prof_sleight_of_hand", "prof_stealth",
                "prof_arcana", "prof_history", "prof_investigation", "prof_nature",
                "prof_religion", "prof_animal_handling", "prof_insight", "prof_medicine",
                "prof_perception", "prof_survival", "prof_deception", "prof_intimidation",
                "prof_performance", "prof_persuasion",
            )
        }),
        ("Спасброски", {
            "classes": ("collapse",),
            "fields": (
                "prof_str_save", "prof_dex_save", "prof_con_save",
                "prof_int_save", "prof_wis_save", "prof_cha_save",
            )
        }),
        ("Снаряжение и магия", {
            "fields": ("equipment", "languages", "tool_proficiencies", "gold", "spells")
        }),
        ("Дополнительно", {
            "fields": ("features", "concept_origin", "backstory")
        }),
        ("Служебные поля", {
            "classes": ("collapse",),
            "fields": ("proficiency_bonus_display", "created_at", "updated_at")
        }),
    )

    @admin.display(description="Бонус мастерства")
    def proficiency_bonus_display(self, obj):
        return obj.proficiency_bonus


@admin.register(AIConceptLog)
class AIConceptLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "prompt")
    readonly_fields = ("created_at",)
    raw_id_fields = ("user",)
    ordering = ("-created_at",)


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rus_name", "speed", "size")
    search_fields = ("name", "rus_name")
    list_filter = ("size",)
    ordering = ("name",)


@admin.register(CharClass)
class CharClassAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rus_name", "hit_die", "skill_slots")
    search_fields = ("name", "rus_name")
    ordering = ("name",)