from rest_framework.pagination import PageNumberPagination


class RecipesLimitPagination(PageNumberPagination):
    page_size_query_param = 'recipes_limit'
    page_size = 5
