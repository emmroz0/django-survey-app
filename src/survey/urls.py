from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("begin-survey/", views.begin_survey, name="begin_survey"),
    path("questionnaire/", views.questionnaire_view, name="questionnaire"),
    path("user-info/", views.user_info_view, name="user_info"),
    path("habits/", views.habits_view, name="habits_view"),
    path("thank-you/", views.thank_you_view, name="thank_you"),
]
