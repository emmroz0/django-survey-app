from django.contrib import admin

from .models import Answer, Habits, Question, SFVPlatform, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "age",
        "gender",
        "education",
        "is_watching_SFV",
        "is_on_mobile",
        "added_at",
    )
    list_filter = ("gender", "education", "is_watching_SFV", "is_on_mobile")
    search_fields = ("education",)


@admin.register(Habits)
class HabitsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "daily_SFV_time",
    )
    list_filter = ("user",)
    search_fields = ("user__id",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "category",
        "question_text",
    )
    search_fields = ("question_text",)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "question",
        "answer",
        "created_at",
    )
    list_filter = ("question__category", "created_at")
    search_fields = ("user__id", "question__question_text")


@admin.register(SFVPlatform)
class SFVPlatformAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
