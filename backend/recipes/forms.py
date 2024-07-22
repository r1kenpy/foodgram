from django.forms import ModelChoiceField


class IngredientChoiceField(ModelChoiceField):
    def label_from_instance(self, ingredient):
        return f'{ingredient} ({ingredient.measurement_unit})'
