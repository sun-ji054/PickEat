from django.urls import path
from .views import (
    KeywordOptionsView,
    RecommendView,
    MyPicksView,
    RestaurantDetailView,
    SaveRestaurantView,
)

urlpatterns = [
    path('restaurants/keywords/',            KeywordOptionsView.as_view(),  name='keyword_options'),
    path('restaurants/recommend/',           RecommendView.as_view(),       name='recommend'),
    path('restaurants/my-picks/',            MyPicksView.as_view(),         name='my_picks'),
    path('restaurants/<str:naver_id>/',      RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('restaurants/<str:naver_id>/save/', SaveRestaurantView.as_view(),  name='save_restaurant'),
]