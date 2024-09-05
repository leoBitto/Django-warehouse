from django.utils import timezone


def calculate_gross_margin(objs):
    total_gross_margin = 0
    for obj in objs:
        total_gross_margin = (total_gross_margin + (obj.unit_price - obj.product.average_purchase_price)) / 2
    return total_gross_margin


# Helper per gli intervalli di date
def get_today():
    return timezone.now().date()

def get_week_params(today):
    start_of_week = today - timezone.timedelta(days=today.weekday())
    end_of_week = start_of_week + timezone.timedelta(days=6)
    return {'week': today.isocalendar()[1], 'year': today.year}, [start_of_week, end_of_week]

def get_month_params(today):
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)
    return {'month': today.month, 'year': today.year}, [start_of_month, end_of_month]

def get_quarter_params(today):
    quarter = (today.month - 1) // 3 + 1
    start_of_quarter = timezone.datetime(today.year, 3 * quarter - 2, 1).date()
    end_of_quarter = (timezone.datetime(today.year, 3 * quarter + 1, 1) - timezone.timedelta(days=1)).date()
    return {'quarter': quarter, 'year': today.year}, [start_of_quarter, end_of_quarter]

def get_year_params(today):
    start_of_year = today.replace(month=1, day=1)
    end_of_year = today.replace(month=12, day=31)
    return {'year': today.year}, [start_of_year, end_of_year]
