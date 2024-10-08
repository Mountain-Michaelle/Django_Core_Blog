from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
# Create your views here.



def post_list(request, tag_slug=None):
    
    post_list = Post.published.all()
    tag = None
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
        
        
    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    
        
    try:
        posts = paginator.page(page_number)
        
    except PageNotAnInteger:
        posts = paginator.page(1)
        
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {'posts': posts, 'tag': tag}
    return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             )
    
    comments = post.comments.filter(active=True)
    
    #List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    
    #form for users to comment
    form = CommentForm()
    context = {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts}
    
    return render(request, 'blog/post/detail.html', context)



def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    form = EmailPostForm(request.POST)
    
    if request.method == 'POST':
        if form.is_valid():
            #form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            
            subject = f"{cd['name']} recommends you read {post.title}" 
            
            message = f" Read {post.title} at {post_url}\n\n" \
                        f"{cd['name']}\'s comments: {cd['comment']}"
            
            send_mail(subject, message, 'debees24@gmail.com', [cd['to']])
            
            sent = True
            
        else:
            form = EmailPostForm()
            
    context = {'post': post, 'form': form, 'sent': sent}
    return render(request, 'blog/post/share.html', context)


def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    
    # A comment was posted
    if form.is_valid():
        #Create a comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
            
    context = {'form': form, 'post': post, 'comment': comment}
    return render(request, 'blog/post/comment.html', context)


def post_search(request):
    search_form = SearchForm()
    query = None
    results = []
    
    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            search_vector =  SearchVector('title', weight='A') + SearchVector('body', weight='B') 
            search_query = SearchQuery(query)
            results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')

            # results = Post.published.annotate(similarity=TrigramSimilarity('title', query),
            #                                 ).filter(similarity__gt=0.1).order_by('-similarity')\
                
    context = {'search_form':search_form, 'query':query, 'results':results}
    return render(request, 'blog/post/blog_search.html', context)

# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'
