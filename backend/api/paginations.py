from rest_framework.pagination import PageNumberPagination


class LimitSizePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 10
    max_page_size = 100


class RecipesLimitPagination(LimitSizePagination):
    page_size_query_param = 'recipes_limit'
    page_size = 5
