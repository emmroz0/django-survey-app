from django.db import models


class VerbalFluencyCategory(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Kategoria",
    )

    class Meta:
        verbose_name = "Kategoria fluencji werbalnej"
        verbose_name_plural = "Kategorie fluencji werbalnej"

    def __str__(self):
        return self.name


class VerbalFluencyTrial(models.Model):
    letter = models.CharField(
        max_length=1,
        verbose_name="Litera",
    )
    category = models.ForeignKey(
        VerbalFluencyCategory,
        on_delete=models.CASCADE,
        related_name="trials",
        verbose_name="Kategoria",
    )
    time_limit = models.PositiveIntegerField(
        default=60,
        verbose_name="Limit czasu (s)",
    )

    class Meta:
        verbose_name = "Próba fluencji werbalnej"
        verbose_name_plural = "Próby fluencji werbalnej"
        unique_together = ("letter", "category")

    def __str__(self):
        return f"{self.letter} - {self.category.name}"


class VerbalFluencyResult(models.Model):
    user = models.ForeignKey(
        "survey.User",
        on_delete=models.CASCADE,
        related_name="verbal_fluency_results",
        verbose_name="Uczestnik",
    )
    trials_data = models.JSONField(
        verbose_name="Dane prób",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data utworzenia",
    )

    class Meta:
        verbose_name = "Wynik fluencji werbalnej"
        verbose_name_plural = "Wyniki fluencji werbalnej"

    def __str__(self):
        return f"Fluencja {self.user.id}"[:50]


class DigitSpanResult(models.Model):
    user = models.ForeignKey(
        "survey.User",
        on_delete=models.CASCADE,
        related_name="digit_span_results",
        verbose_name="Uczestnik",
    )
    span = models.PositiveIntegerField(verbose_name="Długość sekwencji")
    sequence = models.CharField(max_length=255, verbose_name="Sekwencja cyfr")
    user_answer = models.CharField(max_length=255, verbose_name="Odpowiedź uczestnika")
    correct = models.BooleanField(verbose_name="Poprawna odpowiedź")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")

    class Meta:
        verbose_name = "Wynik Digit Span"
        verbose_name_plural = "Wyniki Digit Span"

    def __str__(self):
        return f"DigitSpan {self.user.id} — span {self.span} — {'OK' if self.correct else 'FAIL'}"


class SARTResult(models.Model):
    user = models.ForeignKey(
        "survey.User",
        on_delete=models.CASCADE,
        related_name="sart_results",
        verbose_name="Uczestnik",
    )
    commission_errors = models.PositiveIntegerField(verbose_name="Błędy komisji")
    omission_errors = models.PositiveIntegerField(verbose_name="Błędy pominięcia")
    mean_reaction_time = models.FloatField(
        verbose_name="Średni czas reakcji (ms)", null=True, blank=True
    )
    trials_data = models.JSONField(verbose_name="Dane prób")
    sequence = models.CharField(max_length=255, verbose_name="Sekwencja cyfr")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")

    class Meta:
        verbose_name = "Wynik SART"
        verbose_name_plural = "Wyniki SART"

    def __str__(self):
        return f"SART {self.user.id} — komisja: {self.commission_errors}, pominięcia: {self.omission_errors}"
