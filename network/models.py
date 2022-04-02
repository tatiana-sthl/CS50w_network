from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("self", blank=True, related_name='followers', symmetrical=False)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(User, blank=True, related_name="likes")

    def __str__(self):
        return f"{self.author} posted {self.content}"

    def likes(self):
        return self.liked_by.all().count()

    class Meta: 
        ordering = ['-created_at']

def previous_url(page):
    if page.has_previous(): 
        previous_url = f'?page={page.previous_page_number()}'
    else: 
        previous_url = ''
    return previous_url

def next_url(page):
    if page.has_next():
        next_url = f'?page={page.next_page_number()}'
    else:
        next_url = ''
    return next_url