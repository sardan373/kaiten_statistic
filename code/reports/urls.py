from django.urls import re_path

from reports.views import SimpleStatisticView

urlpatterns = [
    re_path(r"^simple/(?P<user_id>\d+)$", SimpleStatisticView.as_view()),
]
