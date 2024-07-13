import io

from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def create_pdf_shopping_list(ingridients, recipe_in_shopping_cart):
    """Скачивание файла со списком и количеством ингредиентов."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    text = c.beginText()
    text.setTextOrigin(20, 20)
    # pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    # text.setFont('DejaVuSans', 14)
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    text.setFont('Arial', 12)
    if ingridients:
        recipe_in_shopping_cart = ', '.join(recipe_in_shopping_cart)
        text.textLine(
            f'Список покупок на {timezone.now().date()} '
            f'для {recipe_in_shopping_cart}: '
        )
        text.textLines('')
        for ingridient in ingridients:
            text.textLines(ingridient)
    else:
        text.textLine('Список покупок пуст!')
    c.drawText(text)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf
