from django.core.paginator import Paginator
from django.views.generic import ListView

SHOW_POSTS = 10


def page_create(request, posts):
    paginator = Paginator(posts, SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

# class DataMixin:
#     def get_user_context(self):