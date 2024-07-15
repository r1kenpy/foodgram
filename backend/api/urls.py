from django.conf import settings
from django.urls import include, path

from api.views import IngredientVeiwSet, RecipeViewSet, TagViewSet, UserViewSet

if settings.DEBUG:
    from rest_framework.routers import DefaultRouter as Router
else:
    from rest_framework.routers import SimpleRouter as Router

router = Router()

router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientVeiwSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
