from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.utils.text import slugify
from django.db.models import Q
# 추가되는 코드
from .serializers import PostSerializer
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token



class PostList(ListView):
    model = Post
    ordering = '-pk'
    # template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all().order_by('-name')
        context['no_category_post_count'] = Post.objects.filter(
            category=None).count()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        search_keyword = self.request.GET.get('q')

        if search_keyword:
            # queryset = queryset.filter(title__icontains=search_keyword)
            # distinct()는 중복을 제거합니다.
            # Q는 |(or), &(and), ~(not) 연산자를 사용할 수 있습니다.
            # icontains는 대소문자를 구분하지 않는 검색입니다.
            queryset = queryset.filter(
                Q(title__icontains=search_keyword) | Q(content__icontains=search_keyword) | Q(tags__name__icontains=search_keyword)).distinct()

        return queryset

# 추가되는 코드
@api_view(['GET', 'POST'])
def postlistdata(request):
    if request.method == 'GET':
        post_list = Post.objects.all()
        serializer = PostSerializer(post_list, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        print(request.data)
        print(request.user)
        print(request.user.is_authenticated)
        print(request.user.is_anonymous)
        # Bearer로 함께 전송된 token을 가져옵니다.
        token = request.headers.get('Authorization', None)
        print(token)
        # token이 존재하면
        if token:
            print('토큰 존재!')
            try:
                token_key = token.split()[1]
                # 유효한 토근인지 확인합니다. 아래 코드에서 token이 유효하지 않으면 애러 발생하면 except로 넘어갑니다.
                token = Token.objects.get(key=token_key)
                print('사용자:', token.user.username)
                serializer = PostSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response({'error': 'Token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(DetailView):
    model = Post
    # template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('-name')
        context['no_category_post_count'] = Post.objects.filter(
            category=None).count()
        context['comment_form'] = CommentForm
        return context


def category_page(request, slug):
    category = Category.objects.get(slug=slug)
    categories = Category.objects.all().order_by('-name')
    context = {
        'post_list': Post.objects.filter(category=category).order_by('-pk'),
        'categories': categories,
        'no_category_post_count': Post.objects.filter(category=None).count(),
        'category': category,
        'category_list': Category.objects.all().order_by('-name'),
    }
    return render(request, 'blog/post_list.html', context)


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    print(tag)
    post_list = tag.post_set.all()
    categories = Category.objects.all().order_by('-name')
    context = {
        'post_list': post_list,
        'categories': categories,
        'no_category_post_count': Post.objects.filter(category=None).count(),
        'tag': tag,
        'category_list': Category.objects.all().order_by('-name'),
    }
    return render(request, 'blog/post_list.html', context)


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'head_image',
              'file_upload', 'category']

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            # 원래 기존에 리턴하던 값을 response에 담아둡니다.
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')
                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    # self.object는 새로만든 Post 객체
                    self.object.tags.add(tag)
            return response
        else:
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'head_image',
              'file_upload', 'category', 'tags']

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            return super(PostUpdate, self).form_valid(form)
        else:
            return redirect('/blog/')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            post = self.get_object()
            if post.author == request.user:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponse('You are not allowed to update this post')
        return super().dispatch(request, *args, **kwargs)


def new_comment(request, pk):
    if request.user.is_authenticated:
        post = Post.objects.get(pk=pk)
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                # commit=False를 하면, DB에 바로 저장되지 않습니다.
                # 대신, 메모리에 Comment 객체를 하나 생성해 줍니다.
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            form = CommentForm()
        return render(request, 'blog/comment_form.html', {'form': form})


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            return super(CommentUpdate, self).form_valid(form)
        else:
            return redirect('/blog/')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            comment = self.get_object()
            if comment.author == request.user:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponse('You are not allowed to update this comment')
        return super().dispatch(request, *args, **kwargs)


def delete_comment(request, pk):
    if request.user.is_authenticated:
        comment = Comment.objects.get(pk=pk)
        if comment.author == request.user:
            comment.delete()
            return redirect(comment.post.get_absolute_url())
        else:
            return HttpResponse('You are not allowed to delete this comment')
    return redirect('/blog/')


postlist = PostList.as_view()
postdetail = PostDetail.as_view()
write = PostCreate.as_view()
edit = PostUpdate.as_view()
delete = DeleteView.as_view()
update_comment = CommentUpdate.as_view()