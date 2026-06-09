import json
import anthropic
import google.generativeai as genai
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Restaurant, SavedRestaurant
from .serializers import (
    RestaurantSerializer,
    SavedRestaurantSerializer,
    RecommendRequestSerializer,
)
from .constants import FOOD_TYPES, MOODS, DISTANCES, MEAL_SITUATIONS


class KeywordOptionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'food_types':      FOOD_TYPES,
            'moods':           MOODS,
            'distances':       DISTANCES,
            'meal_situations': MEAL_SITUATIONS,
        })


class RecommendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        req_ser = RecommendRequestSerializer(data=request.data)
        if not req_ser.is_valid():
            return Response(req_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        data                = req_ser.validated_data
        food_types          = data['food_types']
        moods               = data['moods']
        distance            = data['distance']
        meal_situation      = data['meal_situation']
        excluded_naver_ids  = data.get('excluded_naver_ids', [])

        restaurants_qs = Restaurant.objects.exclude(naver_id__in=excluded_naver_ids).values('naver_id', 'name')
        restaurant_list_str = '\n'.join(
            f'{r["naver_id"]},{r["name"]}' for r in restaurants_qs
        )

        if not restaurant_list_str:
            return Response(
                {'error': '식당 데이터가 없습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        conditions = []
        if food_types:
            conditions.append(f'음식 종류: {", ".join(food_types)}')
        if moods:
            conditions.append(f'분위기: {", ".join(moods)}')
        if distance and distance != '상관없음':
            conditions.append(f'거리: {distance}')
        if meal_situation:
            conditions.append(f'식사 상황: {meal_situation}')

        prompt = f"""식당 목록 (naver_id,이름):
{restaurant_list_str}

조건: {', '.join(conditions)}

조건에 맞는 식당 3곳을 골라 아래 JSON으로만 응답하세요:
{{"recommendations": [
  {{"rank": 1, "naver_id": "...", "name": "...", "reason": "20자 이내"}},
  {{"rank": 2, "naver_id": "...", "name": "...", "reason": "20자 이내"}},
  {{"rank": 3, "naver_id": "...", "name": "...", "reason": "20자 이내"}}
]}}"""

        try:
            # client  = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            # message = client.messages.create(
            #     model='claude-opus-4-5',
            #     max_tokens=500,
            #     messages=[{'role': 'user', 'content': prompt}],
            # )
            # raw       = message.content[0].text.strip()
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model   = genai.GenerativeModel('gemini-flash-latest')
            message = model.generate_content(prompt)
            raw     = message.text.strip()

            ai_result = json.loads(raw)
            ai_recs   = ai_result.get('recommendations', [])

        except json.JSONDecodeError:
            return Response(
                {'error': 'AI 응답 파싱 오류가 발생했습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {'error': f'AI 추천 중 오류가 발생했습니다: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        result   = []
        used_ids = []

        for rec in ai_recs:
            naver_id = str(rec.get('naver_id', '')).strip()
            try:
                restaurant     = Restaurant.objects.get(naver_id=naver_id)
                data           = RestaurantSerializer(restaurant, context={'request': request}).data
                data['rank']   = rec['rank']
                data['reason'] = rec.get('reason', '')
                result.append(data)
                used_ids.append(restaurant.id)
            except Restaurant.DoesNotExist:
                continue

        # 3개 미만이면 랜덤 보충
        if len(result) < 3:
            extras = (
                Restaurant.objects
                .exclude(id__in=used_ids)
                .exclude(naver_id__in=excluded_naver_ids)
                .order_by('?')[:3 - len(result)]
            )
            for restaurant in extras:
                data           = RestaurantSerializer(restaurant, context={'request': request}).data
                data['rank']   = len(result) + 1
                data['reason'] = '오늘의 추천 맛집'
                result.append(data)
                used_ids.append(restaurant.id)

        return Response({'recommendations': result})


class RestaurantDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, naver_id):
        try:
            restaurant = Restaurant.objects.get(naver_id=naver_id)
        except Restaurant.DoesNotExist:
            return Response(
                {'error': '식당을 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(RestaurantSerializer(restaurant, context={'request': request}).data)


class SaveRestaurantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, naver_id):
        try:
            restaurant = Restaurant.objects.get(naver_id=naver_id)
        except Restaurant.DoesNotExist:
            return Response({'error': '식당을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        _, created = SavedRestaurant.objects.get_or_create(
            user=request.user, restaurant=restaurant
        )
        if not created:
            return Response({'message': '이미 저장된 식당입니다.', 'saved': True})
        return Response({'message': '저장되었습니다.', 'saved': True}, status=status.HTTP_201_CREATED)

    def delete(self, request, naver_id):
        try:
            restaurant = Restaurant.objects.get(naver_id=naver_id)
        except Restaurant.DoesNotExist:
            return Response({'error': '식당을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        deleted, _ = SavedRestaurant.objects.filter(
            user=request.user, restaurant=restaurant
        ).delete()
        if not deleted:
            return Response({'error': '저장된 식당이 아닙니다.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': '저장이 취소되었습니다.', 'saved': False})


class MyPicksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved = (
            SavedRestaurant.objects
            .filter(user=request.user)
            .select_related('restaurant')
        )
        return Response({
            'count':   saved.count(),
            'results': SavedRestaurantSerializer(saved, many=True, context={'request': request}).data,
        })