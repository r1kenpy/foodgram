from django.conf import settings
from django.urls import include, path

from .views import IngredientVeiwSet, TagViewSet

if settings.DEBUG:
    from rest_framework.routers import DefaultRouter as Router
else:
    from rest_framework.routers import SimpleRouter as Router

router_v1 = Router()


router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredient', IngredientVeiwSet, basename='ingredient')

urlpatterns = [path('', include(router_v1.urls))]
