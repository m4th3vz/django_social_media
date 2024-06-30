# models.py
from django.db import models
from django.contrib.auth.models import User

# Definindo um formulário personalizado para o perfil
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username

# Definindo um formulário personalizado para comentários
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.content[:20]
