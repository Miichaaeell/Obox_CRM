from django import template

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
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
        ]
        return f"{meses[month - 1]}/{year}"
    except Exception:
        return value


@register.filter
def calculate_lucrativity(receit, despes):
    """Calcula a lucratividade como (receit - despes) / receit * 100."""
    try:
        receit = float(receit)
        despes = float(despes)
        if receit == 0:
            return "0.00"
        lucrativity = ((receit - despes) / receit) * 100
        return f"{lucrativity:.2f}"
    except (ValueError, TypeError):
        return "0.00"


@register.filter
def subtract(value, arg):
    """Subtrai arg de value."""
    try:
        result = float(value) - float(arg)
        return f"{result:.2f}"
    except (ValueError, TypeError):
        return 0
