


def calculate_gross_margin(objs):
    total_gross_margin = 0
    for obj in objs:
        total_gross_margin = (total_gross_margin + (obj.unit_price - obj.product.average_purchase_price)) / 2
    return total_gross_margin



