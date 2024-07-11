from django.conf import settings
from django.urls import include, path

from api.views import IngredientVeiwSet, RecipeViewSet, TagViewSet, UserViewSet

if settings.DEBUG:
    from rest_framework.routers import DefaultRouter as Router
else:
    from rest_framework.routers import SimpleRouter as Router

router_v1 = Router()

router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientVeiwSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('', include('recipes.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
