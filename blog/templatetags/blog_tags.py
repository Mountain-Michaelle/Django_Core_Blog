from django import template
from ..models import Post
from django.db.models import Count
from ..forms import SearchForm
from django.contrib.postgres.search import SearchVector
from django.shortcuts import render, get_object_or_404


register = template.Library()

@register.simple_tag(name='blog_tags')
def total_posts():
    return Post.published.count()

# Showing latest posts
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

# Showing the most commented posts
@register.simple_tag(name='most_commented')
def get_most_commented_posts(count=3):
    return Post.published.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]
    

# @register.inclusion_tag('blog/post/search.html')
# def post_search_tag(request):
    
#     search_form = SearchForm()
#     query = None
#     results = []
    
#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             results = Post.published.annotate(search=SearchVector('title', 'body'),).filter(search=query)
            
    
#     context = {'search_form': search_form, 'query':query, 'results':results}
#     return render(request, 'blog/post/search.html', context)