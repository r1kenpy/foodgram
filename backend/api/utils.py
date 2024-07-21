import io
from textwrap import wrap

from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def create_pdf_shopping_list(recipes, ingridients):
    """Скачивание файла со списком и количеством продуктов."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    text = c.beginText()
    text.setTextOrigin(20, 20)
    # pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    # text.setFont('DejaVuSans', 14)
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    text.setFont('Arial', 14)
    recipes_cart = [f'{recipe.recipe.name}' for recipe in recipes]
    if ingridients:
        ingridients_cart = [
            (
                f'{ingridient["name"]}({ingridient["measurement_unit"]}):'
                f' {ingridient["amount"]}'
            )
            for ingridient in ingridients
        ]
        recipes_cart = (
            f'Список покупок на {timezone.now().date()} для: '
            + ' \n'.join(recipes_cart)
        )
        wraped = '\n'.join(wrap(recipes_cart, 80))
        ingridients_cart = '\n'.join(ingridients_cart)
        text.textLines(wraped)

        text.textLine('-----' * 25)
        text.textLine('Нужно купить продукты:')
        text.textLine('')
        text.textLines(ingridients_cart)
    else:
        text.textLine('Список покупок пуст!')
    c.drawText(text)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf
