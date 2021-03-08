from django import template

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name='media')
def media(list_items, serie):
    sum_total = 0
    items_quantity = len(list_items)

    for item in list_items:
        try:
            sum_total = sum_total + float(item.__dict__[f'{serie}'])
        except TypeError:
            items_quantity = items_quantity - 1

    average = sum_total / items_quantity

    return round(average, 2)
