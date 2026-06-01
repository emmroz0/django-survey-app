from datetime import datetime
from uuid import uuid4

from django.db import models


class User(models.Model):
    """
    Model przechowujący informacje o uczestniku badania.
    """

    class Gender(models.TextChoices):
        MALE = "male", "Mężczyzna"
        FEMALE = "female", "Kobieta"
        OTHER = "other", "Inna"

    class Education(models.TextChoices):
        PRIMARY = "primary", "Podstawowe"
        SECONDARY = "secondary", "Średnie"
        HIGHER = "higher", "Wyższe"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    age = models.PositiveIntegerField(
        verbose_name="Wiek",
        null=False,
    )

    gender = models.CharField(
        max_length=16,
        choices=Gender.choices,
        verbose_name="Płeć",
        null=False,
    )

    education = models.CharField(
        max_length=16,
        choices=Education.choices,
        verbose_name="Wykształcenie",
        null=False,
    )

    is_watching_SFV = models.BooleanField(
        verbose_name="Czy ogląda KFW",
        null=False,
    )

    is_on_mobile = models.BooleanField(
        default=False,
        verbose_name="Czy korzysta z urządzenia mobilnego",
        null=False,
    )

    added_at = models.DateTimeField(
        default=datetime.now,
        verbose_name="Data dodania",
        null=False,
    )

    class Meta:
        verbose_name = "Uczestnik"
        verbose_name_plural = "Uczestnicy"

    def __str__(self):
        return f"Uczestnik {self.id}"


class SFVPlatform(models.Model):
    """
    Model przechowujący informacje o platformie KFW.
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nazwa platformy",
        null=False,
    )

    class Meta:
        verbose_name = "Platforma KFW"
        verbose_name_plural = "Platformy KFW"

    def __str__(self):
        return self.name


class ContentType(models.Model):
    """
    Model przechowujący informacje o typie treści KFW.
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nazwa typu treści",
        null=False,
    )

    class Meta:
        verbose_name = "Typ treści KFW"
        verbose_name_plural = "Typy treści KFW"

    def __str__(self):
        return self.name


class Habits(models.Model):
    """
    Model przechowujący informacje o nawykach uczestnika badania.
    """

    class DailySFVTime(models.IntegerChoices):
        ZERO_TO_HALF = 15, "Poniżej 0,5 godziny"
        HALF_TO_ONE = 30, "Od 0,5 do 1 godziny"
        ONE_TO_TWO = 90, "Od 1 do 2 godzin"
        TWO_TO_THREE = 150, "Od 2 do 3 godzin"
        THREE_TO_FIVE = 240, "Od 3 do 5 godzin"
        FIVE_PLUS = 360, "Powyżej 5 godzin"

    class DailySFVSessions(models.IntegerChoices):
        ONE_TO_TWO = 2, "Od 1 do 2 sesji"
        THREE_TO_FIVE = 4, "Od 3 do 5 sesji"
        SIX_TO_TEN = 8, "Od 6 do 10 sesji"
        TEN_PLUS = 12, "Powyżej 10 sesji"

    id = models.AutoField(primary_key=True)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Uczestnik",
        null=False,
    )

    daily_SFV_time = models.IntegerField(
        choices=DailySFVTime.choices,
        verbose_name="Średni łączny czas spędzany na KFW dziennie",
        null=False,
    )

    daily_SFV_sessions = models.IntegerField(
        choices=DailySFVSessions.choices,
        verbose_name="Średnia liczba sesji KFW dziennie",
        null=False,
    )

    preferred_platforms = models.ManyToManyField(
        SFVPlatform,
        verbose_name="Preferowane platformy KFW",
    )

    preferred_content_types = models.ManyToManyField(
        ContentType,
        verbose_name="Preferowane treści",
    )

    class Meta:
        verbose_name = "Nawyki"
        verbose_name_plural = "Nawyki"

    def __str__(self):
        return f"Nawyki uczestnika {self.user.id}"


class AnswerOption(models.Model):
    """
    Model przechowujący informacje o opcji odpowiedzi dla pytania jednokrotnego wyboru.
    """

    id = models.AutoField(primary_key=True)
    value = models.PositiveIntegerField(
        verbose_name="Kolejność opcji",
        null=False,
    )

    label = models.CharField(
        max_length=255,
        verbose_name="Tekst opcji",
        null=False,
    )

    class Meta:
        verbose_name = "Opcja odpowiedzi"
        verbose_name_plural = "Opcje odpowiedzi"

    def __str__(self):
        return f"Opcja: {self.label}"


class Question(models.Model):
    """
    Model przechowujący informacje o pytaniu jednokrotnego wyboru.
    """

    id = models.AutoField(primary_key=True)
    category = models.CharField(
        max_length=255,
        verbose_name="Kategoria",
        null=False,
    )
    question_text = models.CharField(
        max_length=255,
        verbose_name="Treść pytania",
        null=False,
    )

    answer_options = models.ManyToManyField(
        AnswerOption,
        verbose_name="Opcje odpowiedzi",
    )

    class Meta:
        verbose_name = "Pytanie"
        verbose_name_plural = "Pytania"

    def __str__(self):
        return f"{self.category}: {self.question_text}"


class Answer(models.Model):
    """
    Model przechowujący odpowiedź użytkownika na pytanie kwestionariusza.
    """

    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Pytanie",
        null=False,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="questionnaire_answers",
        verbose_name="Użytkownik",
        null=False,
    )
    answer = models.CharField(
        max_length=255,
        verbose_name="Odpowiedź",
        null=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data utworzenia",
        null=False,
    )

    class Meta:
        verbose_name = "Odpowiedź"
        verbose_name_plural = "Odpowiedzi"
        unique_together = ("question", "user")

    def __str__(self):
        return f"Odpowiedź: {self.user.id} - {self.question.question_text}"
