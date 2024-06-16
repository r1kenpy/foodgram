from django.conf import settings
from django.urls import include, path

from .views import (
    IngredientVeiwSet,
    TagViewSet,
    RecipeViewSet,
    CustomUserViewSet,
    UserSignInAPIView,
)

if settings.DEBUG:
    from rest_framework.routers import DefaultRouter as Router
else:
    from rest_framework.routers import SimpleRouter as Router

router_v1 = Router()

router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientVeiwSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
    # path('auth/', include('djoser.urls')),
    path('auth/token/login/', UserSignInAPIView.as_view(), name='user-signin'),
    path('auth/', include('djoser.urls.jwt')),
]
