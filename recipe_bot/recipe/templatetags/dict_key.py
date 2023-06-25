from django import template

register = template.Library()


def dict_key(d, k):
    """Returns the given key from a dictionary"""
    return d[k]


register.filter('dict_key', dict_key)
