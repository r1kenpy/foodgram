from django.urls import path

from recipes.views import ShortLinkView

app_name = 'recipes'

urlpatterns = [
    path('<str:encode_id>/', ShortLinkView.as_view(), name='shortlink'),
]
