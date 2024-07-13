from django.db import models

# Create your models here.
from django.db import models


# 对话列表
class ChatList(models.Model):
    gmt_created = models.DateTimeField(auto_now_add=True)
    gmt_modified = models.DateTimeField(auto_now=True)
    userId = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    chat = models.TextField()

    def __str__(self):
        return self.title
