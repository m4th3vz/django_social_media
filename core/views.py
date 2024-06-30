# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileForm, CommentForm
from .models import Profile, Comment
from django.utils import timezone

# Página principal
def index(request):
    return render(request, 'index.html')

# Página de registro
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Cria um perfil vazio para o novo usuário
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

# Exibir perfil
@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    
    # Lógica para lidar com comentários
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
            return redirect('profile')
    else:
        form = CommentForm()
    
    comments = Comment.objects.all().order_by('-created_at')
    
    return render(request, 'profile.html', {'profile': profile, 'form': form, 'comments': comments})

# Editar perfil
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

# Perfil de outros usuários
@login_required
def other_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'profile.html', {'profile': profile})

# Excluir comentário
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        comment.delete()
        return redirect('profile')

# Editar comentário
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
    
    comments = Comment.objects.all().order_by('-created_at')
    profile = Profile.objects.get(user=request.user)
    
    return render(request, 'profile.html', {'form': form, 'comments': comments, 'profile': profile})

