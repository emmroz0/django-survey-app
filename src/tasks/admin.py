from django.contrib import admin

from .models import (
    DigitSpanResult,
    SARTResult,
    VerbalFluencyCategory,
    VerbalFluencyResult,
    VerbalFluencyTrial,
)


@admin.register(DigitSpanResult)
class DigitSpanResultAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "span", "correct", "created_at")
    list_filter = ("correct", "created_at")
    search_fields = ("user__id",)


@admin.register(VerbalFluencyCategory)
class VerbalFluencyCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(VerbalFluencyTrial)
class VerbalFluencyTrialAdmin(admin.ModelAdmin):
    list_display = ("id", "letter", "category", "time_limit")
    list_filter = ("category",)
    search_fields = ("letter",)


@admin.register(VerbalFluencyResult)
class VerbalFluencyResultAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    search_fields = ("user__id",)


@admin.register(SARTResult)
class SARTResultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "commission_errors",
        "omission_errors",
        "mean_reaction_time",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("user__id",)
