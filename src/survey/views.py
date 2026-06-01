from uuid import UUID, uuid4

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from .forms import HabitsForm, QuestionnaireAnswerForm, UserForm
from .models import Answer, Habits, Question, User


@require_GET
def landing_page(request):
    return render(request, "survey/landing_page.html")


@require_GET
def begin_survey(request):
    request.session["survey_user_id"] = str(uuid4())
    return redirect("user_info")


@require_http_methods(["GET", "POST"])
def user_info_view(request):
    survey_user_id = request.session.get("survey_user_id")
    if not survey_user_id:
        return redirect("landing_page")

    if request.method == "POST":
        try:
            user_id = UUID(str(survey_user_id))
        except (TypeError, ValueError):
            request.session.pop("survey_user_id", None)
            return redirect("landing_page")

        form = UserForm(request.POST, instance=User.objects.filter(id=user_id).first())
        if form.is_valid():
            user = form.save(commit=False)
            user.id = user_id
            user.save()
            request.session["survey_user_id"] = str(user.id)
            if form.cleaned_data["is_watching_SFV"]:
                return redirect("habits_view")
            return redirect("questionnaire")
    else:
        try:
            user_id = UUID(str(survey_user_id))
            user_instance = User.objects.filter(id=user_id).first()
            form = UserForm(instance=user_instance)
            return render(request, "survey/survey_base.html", {"form": form})
        except (TypeError, ValueError):
            request.session.pop("survey_user_id", None)
            return redirect("landing_page")


@require_http_methods(["GET", "POST"])
def habits_view(request):
    survey_user_id = request.session.get("survey_user_id")
    if not survey_user_id:
        return redirect("landing_page")

    try:
        user_uuid = UUID(str(survey_user_id))
        user = User.objects.get(id=user_uuid)
    except User.DoesNotExist:
        request.session.pop("survey_user_id", None)
        return redirect("landing_page")
    except (TypeError, ValueError):
        request.session.pop("survey_user_id", None)
        return redirect("landing_page")

    habits_instance = Habits.objects.filter(user=user).first()

    if request.method == "POST":
        form = HabitsForm(request.POST, instance=habits_instance)
        if form.is_valid():
            habits = form.save(commit=False)
            habits.user = user
            habits.save()
            form.save_m2m()
            return redirect("questionnaire")
    else:
        form = HabitsForm(instance=habits_instance)

    return render(request, "survey/survey_base.html", {"form": form})


@require_http_methods(["GET", "POST"])
def questionnaire_view(request):
    survey_user_id = request.session.get("survey_user_id")
    if not survey_user_id:
        return redirect("landing_page")

    try:
        user_uuid = UUID(str(survey_user_id))
        user = User.objects.get(id=user_uuid)
    except User.DoesNotExist:
        request.session.pop("survey_user_id", None)
        return redirect("landing_page")
    except (TypeError, ValueError):
        request.session.pop("survey_user_id", None)
        return redirect("landing_page")

    questions = Question.objects.prefetch_related("answer_options").order_by("id")

    if not questions.exists():
        return JsonResponse(
            {"status": "error", "message": "Nie znaleziono pytań"}, status=404
        )

    if request.method == "POST":
        form = QuestionnaireAnswerForm(questions, request.POST)
        if form.is_valid():
            for question in questions:
                answer_value = form.cleaned_data.get(f"question_{question.id}")
                if answer_value:
                    Answer.objects.update_or_create(
                        question=question,
                        user=user,
                        defaults={"answer": answer_value},
                    )
            return redirect("digit_span")
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)

    form = QuestionnaireAnswerForm(questions)
    return render(
        request,
        "survey/survey_base.html",
        {"form": form, "questions": questions},
    )
