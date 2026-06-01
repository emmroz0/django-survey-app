from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit
from django import forms
from django.urls import reverse

from .models import ContentType, Habits, SFVPlatform, User


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "Informacje o uczestniku"
        self.description = (
            "Proszę o podanie kilku informacji o sobie. Dane te będą wykorzystywane "
            "wyłącznie do celów badawczych."
        )
        self.back_url = reverse("landing_page")

    age = forms.IntegerField(
        min_value=18,
        max_value=99,
        required=True,
        widget=forms.NumberInput(),
        label="Wiek",
    )

    gender = forms.ChoiceField(
        choices=User.Gender.choices,
        required=True,
        widget=forms.RadioSelect(),
        label="Płeć",
    )
    education = forms.ChoiceField(
        choices=User.Education.choices,
        required=True,
        widget=forms.RadioSelect(),
        label="Wykształcenie",
    )

    is_watching_SFV = forms.TypedChoiceField(
        choices=[(True, "Tak"), (False, "Nie")],
        coerce=lambda x: x == "True",
        required=True,
        widget=forms.RadioSelect(),
        label="Czy oglądasz krótkie formy wideo (np. TikTok, Instagram Reels, YouTube Shorts)?",
    )

    class Meta:
        model = User
        fields = ["age", "gender", "education", "is_watching_SFV"]


class HabitsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "Nawyki korzystania z mediów"
        self.description = (
            "Podaj orientacyjny czas korzystania "
            "z mediów oraz preferencje."
        )
        self.back_url = reverse("user_info")

    preferred_platforms = forms.ModelMultipleChoiceField(
        queryset=SFVPlatform.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple(),
        label="Preferowane platformy KFW",
    )

    preferred_content_types = forms.ModelMultipleChoiceField(
        queryset=ContentType.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple(),
        label="Preferowane treści",
    )

    daily_SFV_time = forms.ChoiceField(
        choices=Habits.DailySFVTime.choices,
        required=True,
        widget=forms.RadioSelect(),
        label="Średni łączny czas spędzany na KFW dziennie",
    )

    daily_SFV_sessions = forms.ChoiceField(
        choices=Habits.DailySFVSessions.choices,
        required=True,
        widget=forms.RadioSelect(),
        label="Średnia liczba sesji KFW dziennie",
    )

    class Meta:
        model = Habits
        fields = [
            "preferred_platforms",
            "preferred_content_types",
            "daily_SFV_time",
            "daily_SFV_sessions",
        ]


class QuestionnaireAnswerForm(forms.Form):
    """
    Dynamiczna forma do odpowiadania na pytania z kwestionariusza.
    Tworzona na podstawie list pytań i ich opcji odpowiedzi.
    """

    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = questions
        self.title = "Kwestionariusz"
        self.description = (
            "Prosimy o udzielenie odpowiedzi na poniższe pytania. "
            "Każde pytanie wymaga wybrania jednej odpowiedzi."
        )
        self.back_url = reverse("habits_view")

        for question in questions:
            choices = [
                (str(option.value), option.label)
                for option in question.answer_options.all().order_by("value", "id")
            ]

            field = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(),
                label=question.question_text,
                required=True,
            )
            self.fields[f"question_{question.id}"] = field

        self.helper = FormHelper(self)
        self.helper.form_method = "POST"
        self.helper.form_tag = False
        self.helper.layout = Layout(
            *[Field(f"question_{question.id}") for question in questions],
            Div(
                Submit(
                    "submit",
                    "Wyślij odpowiedzi",
                    css_class="btn btn-primary btn-lg px-5",
                ),
                css_class="d-grid d-sm-block",
            ),
        )
