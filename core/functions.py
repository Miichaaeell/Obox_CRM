from datetime import datetime
from django.db.models import Q, Sum
from django.http import JsonResponse
from enterprise.models import Cashier, Bill, Payment

def get_context_cashier_data():
        last_cashier = Cashier.objects.order_by('-created_at').first()
        if last_cashier.status == 'closed':
            context = {
                'status': last_cashier.get_status_display(),
                'income_pix': last_cashier.income_pix,
                'income_credit': last_cashier.income_credit,
                'income_debit': last_cashier.income_debit,
                'income_cash': last_cashier.income_cash,
                'total_incomes': last_cashier.total_incomes,
                'bills': last_cashier.bills.all(),
                'expense_pix': last_cashier.expense_pix,
                'expense_boleto': last_cashier.expense_boleto,
                'expense_automatic': last_cashier.expense_automatic,
                'expense_others': last_cashier.expense_others,
                'expense_withdrawal': last_cashier.expense_withdrawal,
                'total_expenses': last_cashier.total_expenses,
                'payments': last_cashier.payments.all(),
                'date_start': last_cashier.created_at,
                'date_end': last_cashier.date_closing,
                'opening_balance': last_cashier.opening_balance,
                'closing_balance': last_cashier.closing_balance
            }
            return context
        start = last_cashier.created_at
        end = datetime.now()
        payments = Payment.objects.filter(Q(created_at__gte=(start))
                                          | Q(created_at__lte=(end)),
                                          cashier__isnull=True)
        total = payments.aggregate(
            income_pix=Sum('value', filter=Q(payment_method__iexact="pix")),
            income_credit=Sum('value', filter=Q(
                payment_method__iexact="credito")),
            income_debit=Sum('value', filter=Q(
                payment_method__iexact="debito")),
            income_cash=Sum('value', filter=Q(
                payment_method__iexact="dinheiro")),
            total_incomes=Sum('value')
        )
        bill = Bill.objects.select_related(
            'payment_method', 'status').filter(Q(date_payment__gte=(start)) |
                                               Q(date_payment__lte=(end)), cashier__isnull=True)
        pay = bill.filter(Q(status__status__iexact='pago') | Q(payment_method__method__icontains='automatico')).aggregate(
            total_expenses=Sum('value'),
            expense_pix=Sum('value', filter=Q(
                payment_method__method__iexact='pix')),
            expense_boleto=Sum('value', filter=Q(
                payment_method__method__iexact='boleto')),
            expense_automatic=Sum('value', filter=Q(
                payment_method__method__iexact='deb. automatico')),
            expense_others=Sum('value', filter=Q(payment_method__method__iexact='credito') | Q(
                payment_method__method__iexact='debito')),
        )
        income = total['total_incomes'] or 0
        expense = pay['total_expenses'] or 0
        last_balance = Cashier.objects.filter(
            status='closed').order_by('-created_at').first()
        print(last_balance.closing_balance)
        closing_balance = last_balance.closing_balance + income - expense
        expense_withdrawal = last_cashier.expense_withdrawal
        context = {
            'status': last_cashier.get_status_display(),
            'income_pix': total['income_pix'] if total['income_pix'] else 0,
            'income_credit': total['income_credit'] if total['income_credit'] else 0,
            'income_debit': total['income_debit'] if total['income_debit'] else 0,
            'income_cash': total['income_cash'] if total['income_cash'] else 0,
            'total_incomes': total['total_incomes'] if total['total_incomes'] else 0,
            'bills': bill,
            'expense_pix': pay['expense_pix'] if pay['expense_pix'] else 0,
            'expense_boleto': pay['expense_boleto'] if pay['expense_boleto'] else 0,
            'expense_automatic': pay['expense_automatic'] if pay['expense_automatic'] else 0,
            'expense_others': pay['expense_others'] if pay['expense_others'] else 0,
            'expense_withdrawal': expense_withdrawal,
            'total_expenses': pay['total_expenses'] if pay['total_expenses'] else 0,
            'payments': payments,
            'date_start': start,
            'opening_balance': last_balance.closing_balance if last_balance else 0,
            'closing_balance': closing_balance if closing_balance else 0
        }
        return context
    
def create_new_register_cashier():
    try:
        if Cashier.objects.filter(status='open').exists():
            return JsonResponse({'status': 'warning', 'title': 'Abertura de Caixa', 'message': 'Já existe um caixa aberto!'}, status=400)
        last_cashier = Cashier.objects.order_by('-created_at').first()
        new_cashier = Cashier.objects.create(
            opening_balance=last_cashier.closing_balance if last_cashier else 0,
            status='open',
        )
        return JsonResponse({'status': 'success', 'title': 'Abertura de Caixa', 'message': 'Caixa aberto com sucesso!'}, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'title': 'Erro ao abrir caixa', 'message': f'{e}'}, status=400)
    
    
def close_cashier(context, withdrawalValue, closing_balance):
    try:
        last_cashier = Cashier.objects.order_by('-created_at').first()
        last_cashier.status = 'closed'
        last_cashier.date_closing = datetime.now()
        last_cashier.total_incomes = context['total_incomes']
        last_cashier.total_expenses = context['total_expenses'] + withdrawalValue
        last_cashier.closing_balance = closing_balance
        last_cashier.income_pix = context['income_pix']
        last_cashier.income_credit = context['income_credit']
        last_cashier.income_debit = context['income_debit']
        last_cashier.income_cash = context['income_cash']
        last_cashier.expense_pix = context['expense_pix']
        last_cashier.expense_boleto = context['expense_boleto']
        last_cashier.expense_automatic = context['expense_automatic']
        last_cashier.expense_others = context['expense_others']
        last_cashier.expense_withdrawal = withdrawalValue
        last_cashier.save()
        # Atualizar os pagamentos e contas vinculando ao caixa fechado
        context['bills'].update(cashier=last_cashier)
        context['payments'].update(cashier=last_cashier)
        return JsonResponse({'status': 'success', 'title': 'Fechamento do Caixa', 'message': f'Caixa fechado com sucesso! Saldo final R${closing_balance}, Retirado: R${withdrawalValue}'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'title': 'Erro ao fechar Caixa', 'message': str(e)}, status=400)