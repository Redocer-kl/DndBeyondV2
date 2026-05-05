from rest_framework import serializers
from .models import Character

class CharacterSerializer(serializers.ModelSerializer):
    proficiency_bonus = serializers.IntegerField(read_only=True)
    modifiers = serializers.SerializerMethodField()

    class Meta:
        model = Character
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at', 'current_hp')

    def get_modifiers(self, obj):
        """Возвращает словарь модификаторов для всех характеристик"""
        return {
            "str": obj.get_modifier(obj.strength),
            "dex": obj.get_modifier(obj.dexterity),
            "con": obj.get_modifier(obj.constitution),
            "int": obj.get_modifier(obj.intelligence),
            "wis": obj.get_modifier(obj.wisdom),
            "cha": obj.get_modifier(obj.charisma),
        }

    def validate_level(self, value):
        if not (1 <= value <= 20):
            raise serializers.ValidationError("Уровень должен быть от 1 до 20.")
        return value

    def validate(self, data):
        """
        Валидация характеристик. 
        Полезно, если Ollama решит выдать статы выше 20 на 1 уровне.
        """
        stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        for stat in stats:
            val = data.get(stat)
            if val is not None and (val < 1 or val > 30): # 30 - абсолютный максимум в 5e
                raise serializers.ValidationError({stat: "Характеристика должна быть в диапазоне от 1 до 30."})
        return data

    def create(self, validated_data):
        # При создании через ИИ, устанавливаем текущие ХП равными максимальным
        if 'current_hp' not in validated_data and 'max_hp' in validated_data:
            validated_data['current_hp'] = validated_data['max_hp']
        
        # Получаем пользователя из контекста запроса (request.user)
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)