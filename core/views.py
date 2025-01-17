# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileForm, CommentForm
from .models import Profile, Comment, Follow
from django.utils import timezone
from django.db.models import OuterRef, Subquery

# Página principal
def index(request):
    if request.user.is_authenticated:
        # Obter os seguidos e a data em que começaram a ser seguidos
        following = Follow.objects.filter(follower=request.user)
        
        # Obter os comentários dos seguidos, mas apenas aqueles feitos depois de começarem a ser seguidos
        comments = Comment.objects.filter(
            user__in=[follow.followed for follow in following],
            created_at__gte=Subquery(
                Follow.objects.filter(
                    follower=request.user,
                    followed=OuterRef('user')
                ).values('created_at')[:1]
            )
        ).order_by('-created_at')
    else:
        comments = Comment.objects.none()
    
    return render(request, 'index.html', {'comments': comments})

# Página de registro
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Profile.objects.create(user=user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Página de login
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Página do perfil pessoal
@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
            return redirect('profile')
    else:
        form = CommentForm()
    
    comments = Comment.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'profile.html', {'profile': profile, 'form': form, 'comments': comments})

# Página de edição do perfil
@login_required
def profile_edit_view(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile_edit.html', {'form': form})

# Página para o perfil dos outros usuários
@login_required
def other_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    comments = Comment.objects.filter(user=user).order_by('-created_at')
    
    is_following = Follow.objects.filter(follower=request.user, followed=user).exists()
    
    return render(request, 'other_profile.html', {'profile': profile, 'comments': comments, 'is_following': is_following})

# Função para seguir um usuário
@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
    return redirect('other_profile', username=username)

# Função para deixar de seguir um usuário
@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    Follow.objects.filter(follower=request.user, followed=user_to_unfollow).delete()
    return redirect('other_profile', username=username)

# Função para apagar um comentário
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        comment.delete()
        return redirect('profile')
    return redirect('profile')

# Função para editar um comentário
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.edited_at = timezone.now()
            comment.save()
            return redirect('profile')
    else:
        form = CommentForm(instance=comment)
    
    comments = Comment.objects.filter(user=request.user).order_by('-created_at')
    profile = Profile.objects.get(user=request.user)
    
    return render(request, 'profile.html', {'form': form, 'comments': comments, 'profile': profile})

# Página para a lista de seguidores
@login_required
def following_list_view(request):
    following = Follow.objects.filter(follower=request.user)
    followed_users = [follow.followed for follow in following]
    return render(request, 'followingList.html', {'followed_users': followed_users})

# Página para a lista de quem segue você
@login_required
def followed_list_view(request):
    followers = Follow.objects.filter(followed=request.user)
    follower_users = [follow.follower for follow in followers]
    return render(request, 'followedList.html', {'follower_users': follower_users})
