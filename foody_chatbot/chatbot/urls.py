from django.urls import path

from . import views
from .views import (
    TodoListApiView,
    GPTApiView
)
app_name = "chatbot"
urlpatterns = [
    path('api/completion/', GPTApiView.as_view()),
    path('api/', TodoListApiView.as_view()),
    # path("", views.index, name="index"),
    # # ex: /chatbot/5/
    # path("<int:question_id>/", views.detail, name="detail"),
    # # ex: /chatbot/5/results/
    # path("<int:question_id>/results/", views.results, name="results"),
    # # ex: /chatbot/5/vote/
    # path("<int:question_id>/vote/", views.vote, name="vote"),
]