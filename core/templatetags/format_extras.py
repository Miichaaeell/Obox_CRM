from django import template
import calendar

register = template.Library()


@register.filter
def month_name(value):
    """Converte 'YYYY-MM' em 'Mês/YYYY'"""
    try:
        value = str(value)
        # suporta '9/2025' ou '09/2025'
        if "/" in value:
            month, year = value.split("/")
        else:
            year, month = value.split("-")

        month = int(month)
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        return f"{meses[month-1]}/{year}"
    except Exception:
        return value
