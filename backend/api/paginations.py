from rest_framework.pagination import PageNumberPagination


class RecipesLimitPagination(PageNumberPagination):
    page_size_query__param = 'limit'
