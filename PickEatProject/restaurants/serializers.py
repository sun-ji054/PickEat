from rest_framework import serializers
from .models import Restaurant, SavedRestaurant
from .constants import FOOD_TYPES, MOODS, DISTANCES, MEAL_SITUATIONS


class RestaurantSerializer(serializers.ModelSerializer):
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['id', 'naver_id', 'name', 'picture', 'is_saved']

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedRestaurant.objects.filter(
                user=request.user, restaurant=obj
            ).exists()
        return False


class SavedRestaurantSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)

    class Meta:
        model = SavedRestaurant
        fields = ['id', 'restaurant', 'saved_at']


class RecommendRequestSerializer(serializers.Serializer):
    food_types = serializers.ListField(
        child=serializers.ChoiceField(choices=FOOD_TYPES),
        default=list,
    )
    moods = serializers.ListField(
        child=serializers.ChoiceField(choices=MOODS),
        default=list,
    )
    distance = serializers.ChoiceField(
        choices=DISTANCES,
        required=False,
        default='상관없음',
    )
    meal_situation = serializers.ChoiceField(
        choices=MEAL_SITUATIONS,
        required=False,
        allow_blank=True,
        default='',
    )

    def validate(self, data):
        if not data.get('food_types') and not data.get('moods'):
            raise serializers.ValidationError('음식 종류 또는 분위기를 하나 이상 선택해주세요.')
        return data