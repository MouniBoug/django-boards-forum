from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Board, Topic, Post
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.views.generic import UpdateView, ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.utils.decorators import method_decorator # can’t decorate classes directly so use this utility
from .forms import NewTopicForm, PostForm
from django.urls import reverse



# def home(request): => function based view
#     boards = Board.objects.all()
#     return render(request, 'home.html', {'boards': boards})

class BoardListView(ListView): #  generic class based view of the above
    model = Board  # we inherit ListView generic class suz we just retrieve & list boards
    template_name = 'home.html'
    context_object_name = 'boards'

class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_update').annotate(replies=Count('posts') - 1)
        return queryset

@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    # user = User.objects.first() =>  querying the database and picking the first user

    if request.method == 'POST':
        form = NewTopicForm(request.POST) # instantiate a form instance & passing the POST data
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user # get the current loged in user
            topic.save()
            post = Post.objects.create( # the starter post when topic is created
                message=form.cleaned_data.get('message'),
                topic=topic,
                create_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)

    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):

        session_key = 'viewed_topic_{}'.format(self.topic.pk)  # so user view won't count by revist & refresh
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True           

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.create_by = request.user
            post.save()

            topic.last_update = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})




@method_decorator(login_required, name='dispatch') # utility(decorator, methodToDecorate)
class PostUpdateView(UpdateView): # In class-based views it’s common to decorate the dispatch method(internal Django method )
    model = Post
    fields = ('message',) # cuz it's simple form we use fields but if complex us form_class & refer to your form
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk' # indentify the name of the keyword argument used to retrieve the Post object
    context_object_name = 'post' # so we can call Post objects/instances 'post' in templates & not the default 'object'

    def get_queryset(self): # this is for not letting users to access url posts of other users
        queryset = super().get_queryset() # method from the parent class UpateView class
        return queryset.filter(create_by=self.request.user)

    def form_valid(self, form): # we're overriding this func to set extra fields like the updated_by & updated_at
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


