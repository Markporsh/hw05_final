from django.core.paginator import Paginator

SHOW_POSTS = 10


def paginate_posts(request, posts):
    paginator = Paginator(posts, SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
