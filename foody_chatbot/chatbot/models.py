import datetime
from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.utils import timezone

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text
    
class Todo(models.Model):
    task = models.CharField(max_length = 180)
    timestamp = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True)
    completed = models.BooleanField(default = False, blank = True)
    updated = models.DateTimeField(auto_now = True, blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)

    def __str__(self):
        return self.task
    
class Session(models.Model):
    user_id = models.ForeignKey(User, on_delete = models.CASCADE)
    
    
class Message(models.Model):
    session_id = models.ForeignKey(Session, on_delete = models.CASCADE)
    text_message = models.TextField(blank = True, default = "")
    payload = models.JSONField(blank = True)
    role = models.ForeignKey(User, on_delete = models.CASCADE)
