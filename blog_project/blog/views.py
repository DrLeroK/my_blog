from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
# render: Used to render HTML templates with data.
# get_object_or_404: Retrieves an object from the database or returns a 404 error if it does not exist.
# redirect: Redirects the user to another page after an action (like submitting a form).

from django.contrib.auth.decorators import login_required
# login_required: A decorator that ensures a user must be logged in before accessing a specific function-based view.

from django.contrib.auth.mixins import LoginRequiredMixin
# LoginRequiredMixin: A mixin that ensures only authenticated users can access a class-based view.

from django.urls import reverse_lazy
# reverse_lazy: Used to redirect users after an action is completed. 
# Unlike reverse(), it is only evaluated when needed (useful in class-based views)

from django.views.generic import (TemplateView, ListView, 
                                  DetailView, CreateView, 
                                  UpdateView, DeleteView)
# TemplateView: Used for simple static pages.
# ListView: Displays a list of objects.
# DetailView: Displays details of a specific object.
# CreateView: Allows creating a new object.
# UpdateView: Allows editing an object.
# DeleteView: Allows deleting an object.


# local imports
from blog.models import Post, Comment
from blog.forms import PostForm, CommentForm



########################
# Create your views here.
class AboutView(TemplateView):
    template_name = 'about.html'


class PostListView(ListView):
    model = Post

    def get_queryset(self):
        # Filters posts with published_date <= now, ordered newest first
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')


class PostDetailView(DetailView):
    model = Post


class CreatePostView(LoginRequiredMixin, CreateView): 
    login_url = '/login/'  # If a user is not logged in, they will be redirected to the login page.
    redirect_field_name = 'blog/post_detail.html'  # Where to go after login

    form_class = PostForm
    model = Post


    def form_valid(self, form):
        form.instance.author = self.request.user  # Set the author = current user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm
    model = Post


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'  
    success_url = reverse_lazy('post_list')


class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')
        # Only shows drafts (posts without published_date), Oldest first


# Function-based views
@ login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk) # Get post or 404 error if not found
    post.publish()
    return redirect('post_detail', pk=pk)


# Comment Views
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST) # Bind form to submitted data
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post  # Link comment to the post
            comment.save()  # Now save to DB
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()  # Show empty form
    
    return render(request, 'blog/post_comment.html', {'form': form}) 
    # If GET request (just loading the page)
    # Render the comment form template with the empty form


@ login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@ login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk  # Store post PK before deletion
    comment.delete()
    return redirect('post_detail', pk=post_pk)

