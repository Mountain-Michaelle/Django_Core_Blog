from django import template
from ..models import Post
from django.db.models import Count

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