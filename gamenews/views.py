from pydoc import text
import re
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import F, Q, CharField, Count, Max, Case, When, Value
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from gamenews.forms import AddPostForm, CommentForm
from gamenews.models import Category, Comment, Post
from users import views
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

VSEGPT_KEY=os.getenv('VSEGPT_KEY')

def gptiha(text):
    vopros=f'''
    Ты ии модератор для комментариев на сайте. Комментарий должен не упоминать политику, не содержать оскорбленийю Так же в комментарии не должно быть упоминания Лабубу. НИКОГДА
    оцени этот комментарий: {text}

    отвечай только True или False. без лишних слов. Только эти два слова
    '''
    
    

    # Выполнение POST запроса
    response = requests.post(
        "https://api.vsegpt.ru/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {VSEGPT_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openai/gpt-5-nano",
            "messages": [{"role": "user", "content": vopros}]
        }
    )

    # Обработка ответа
    response_data = response.json()
    msg = response_data["choices"][0]["message"]["content"]

    if msg.lower() == 'true':
        #print(f'\n#####\n#####\n ОНО ОТВЕТИЛО {msg}!!!!!!!!!\n####\n####\n#####')
        return True
    elif msg.lower() == 'false':
        #print(f'\n#####\n#####\n ОНО ОТВЕТИЛО {msg}!!!!!!!!!\n####\n####\n#####')
        return False
    else:
        print('\n#####\n#####\n ОНО ОТВЕТИЛО НЕ ТАК!!!!!!!!!\n####\n####\n#####')
class IndexPage(ListView):
    model = Post
    template_name = "gamenews/index.html"
    context_object_name = "posts"
    paginate_by = 3

    def get_queryset(self):
        if self.request.GET:
            if "search" in self.request.GET:
                query = self.request.GET["search"]
                return Post.objects.filter(
                    Q(title__icontains=query) | Q(full_description__icontains=query)
                )

        return Post.objects.annotate(rate=Case(
            When(views__gt=100, then=Value("Высокий")),
            When(views__gt=50, then=Value("Средний")),
            When(views__gt=10, then=Value("Низкий")),
            default=Value("Начальный"),
            output_field=CharField()
        ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Главная страница"
        context["count"] = self.get_queryset().count()
        print(Post.objects.aggregate(max=Max("pk")))
        context["anno"] = Category.objects.annotate(total=Count("posts_by_cat"))
        if self.request.GET:
            if "search" in self.request.GET:
                context["search"] = self.request.GET["search"]
        return context


class DetailPost(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "gamenews/post_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        viewed = self.request.COOKIES.get('views_post')  
        if viewed:
            viewed_list= viewed.split(' ')
            int_viewed_list = list(map(int, viewed_list))
            #context["last_viewed"] = Post.objects.filter(id__in = int_viewed_list)
            context["last_viewed"] = [Post.objects.get(id=x) for x in int_viewed_list]
            print(context["last_viewed"])
        
        
        context["comments"] = post.comments_by_post.filter(verify=True)
        context["title"] = post.title
        context["rel_posts"] = (
            Post.objects.select_related("category")
            .prefetch_related("tag")
            .filter(category=post.category)
            .order_by("?")[:3]
        )
        context["best_cats"] = Category.objects.annotate(
            total=Count("posts_by_cat")
        ).order_by("-total")[:5]
        context["last_posts"] = Post.objects.all().order_by('-published_date')[:3]
        
        
        
        
        return context

    def get(self, request, *args, **kwargs):        
        form = CommentForm()
        self.object = self.get_object()
        Post.objects.filter(pk=self.object.pk).update(views=F("views") + 1)
        self.object.refresh_from_db()
        my_context = self.get_context_data(object=self.object)
        my_context["form"] = form        
        response =self.render_to_response(context=my_context)
        
        viewed = request.COOKIES.get('views_post')
        str_obj=str(self.object.id)
        if viewed:
            viewed_list = viewed.split(' ')
            if str_obj in viewed_list:
                print(str_obj)
                print(viewed_list)
                print("уже есть")
                print("убрал")
                viewed_list.remove(str_obj)
            viewed_list.insert(0, str_obj)
            if len(viewed_list)>5:
                
                viewed_list = viewed_list[:5]
            
        else:
            viewed_list = [str_obj]

        response.set_cookie(key='views_post',value=' '.join(viewed_list), max_age=84600)
        
        return response
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            author = request.user
            if author.username == "admin1":
                verify = True
            else:
                verify = gptiha(form.cleaned_data["text"])
                if verify == True:
                    Comment.objects.update(text=form.cleaned_data["text"]+"(Проверенно с ии)")

            Comment.objects.create(
                post=self.object,
                author=author,
                text=form.cleaned_data["text"],
                verify=verify,
            )

            return redirect(self.object.get_absolute_url())
        context = self.get_context_data(form=form)
        return self.render_to_response(context=context)


class AddPostView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    form_class = AddPostForm
    template_name = "gamenews/form_add.html"

    def form_valid(self, form):
        new_post = form.save(commit=False)
        new_post.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создание поста"
        return context


class UpdatePostView(UpdateView):
    model = Post
    fields = ["title", "shot_description", "full_description"]
    template_name = "gamenews/form_add.html"
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Изменение поста"
        return context


class About(TemplateView):
    template_name = "gamenews/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "О нас"
        return context


class CategoryView(ListView):
    model = Category
    template_name = "gamenews/category_all.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.annotate(post_count=Count("posts_by_cat"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Все категории"
        return context


class CategoryDetailView(ListView):
    model = Post
    template_name = "gamenews/category.html"
    context_object_name = "post_cats"

    def get_queryset(self):
        query_set = super().get_queryset()
        cat = Category.objects.get(slug=self.kwargs["slug"])
        return query_set.filter(category__pk=cat.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cat"] = Category.objects.get(slug=self.kwargs["slug"])
        context["title"] = context["cat"]
        return context
