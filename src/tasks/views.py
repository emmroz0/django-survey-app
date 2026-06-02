import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import (
    DigitSpanResult,
    SARTResult,
    VerbalFluencyResult,
    VerbalFluencyTrial,
)


def digit_span_view(request):
    return render(request, "tasks/digitspan.html")


@require_POST
@csrf_exempt
def digit_span_result_view(request):
    try:
        data = json.loads(request.body)
        user_id = request.session.get("survey_user_id")
        if not user_id:
            return JsonResponse({"error": "Brak identyfikatora uczestnika"}, status=400)

        span = data["span"]
        sequence = "".join(str(d) for d in data["sequence"])

        user_answer = data.get("answer", "")
        correct = user_answer.strip() == sequence

        DigitSpanResult.objects.create(
            user_id=user_id,
            span=span,
            sequence=sequence,
            user_answer=user_answer,
            correct=correct,
        )

        return JsonResponse({"success": True, "correct": correct})
    except (KeyError, TypeError, ValueError) as e:
        return JsonResponse({"error": str(e)}, status=400)


def sart_view(request):
    return render(request, "tasks/sart.html")


@require_POST
@csrf_exempt
def sart_result_view(request):
    try:
        data = json.loads(request.body)
        user_id = request.session.get("survey_user_id")
        if not user_id:
            return JsonResponse({"error": "Brak identyfikatora uczestnika"}, status=400)

        sequence = ",".join(str(d) for d in data["sequence"])
        trials = data["trials"]

        commission_errors = sum(1 for t in trials if t["digit"] == 3 and t["clicked"])
        omission_errors = sum(1 for t in trials if t["digit"] != 3 and not t["clicked"])
        reaction_times = [t["rt_ms"] for t in trials if t["rt_ms"] is not None]
        mean_rt = (
            round(sum(reaction_times) / len(reaction_times), 1)
            if reaction_times
            else None
        )

        SARTResult.objects.create(
            user_id=user_id,
            commission_errors=commission_errors,
            omission_errors=omission_errors,
            mean_reaction_time=mean_rt,
            trials_data=trials,
            sequence=sequence,
        )

        return JsonResponse({"success": True})
    except (KeyError, TypeError, ValueError) as e:
        return JsonResponse({"error": str(e)}, status=400)


def verbal_fluency_view(request):
    trials = (
        VerbalFluencyTrial.objects
        .select_related("category")
        .order_by("id")
    )
    trials_data = [
        {
            "id": t.id,
            "letter": t.letter,
            "category": t.category.name,
            "time_limit": t.time_limit,
        }
        for t in trials
    ]
    return render(request, "tasks/verbalfluency.html", {"trials_json": json.dumps(trials_data)})


@require_POST
@csrf_exempt
def verbal_fluency_result_view(request):
    try:
        data = json.loads(request.body)
        user_id = request.session.get("survey_user_id")
        if not user_id:
            return JsonResponse({"error": "Brak identyfikatora uczestnika"}, status=400)

        VerbalFluencyResult.objects.create(
            user_id=user_id,
            trials_data=data["trials"],
        )

        return JsonResponse({"success": True})
    except (KeyError, TypeError, ValueError) as e:
        return JsonResponse({"error": str(e)}, status=400)
