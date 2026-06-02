from django.urls import path

from . import views

urlpatterns = [
    path("digitspan/", views.digit_span_view, name="digit_span"),
    path("digitspan/result/", views.digit_span_result_view, name="digit_span_result"),
    path("sart/", views.sart_view, name="sart"),
    path("sart/result/", views.sart_result_view, name="sart_result"),
    path("verbalfluency/", views.verbal_fluency_view, name="verbal_fluency"),
    path("verbalfluency/result/", views.verbal_fluency_result_view, name="verbal_fluency_result"),
]
