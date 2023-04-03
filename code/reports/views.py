from collections import defaultdict

from django.shortcuts import render
from django.views.generic import View

from kaiten_tasks.models import KaitenTask, KaitenUser


class SimpleStatisticView(View):
    def get(self, request, user_id):
        user = KaitenUser.objects.filter(id=user_id).first()
        if not user:
            raise Exception("no such user")
        
        tasks_qs = KaitenTask.objects.filter(user=user).order_by("-moved_to_review")

        months = defaultdict(lambda: {"size": 0, "task_list": []})
        progress = {"size": 0, "task_list": []}
        for task in tasks_qs:
            key = (
                task.moved_to_review.strftime("%Y_%m") if task.moved_to_review
                else "progress"
            )

            data = {
                "name": task.name,
                "size": task.size,
                "progress": task.moved_to_progress,
                "review": task.moved_to_review,
            }
            if task.moved_to_review:
                key = task.moved_to_review.strftime("%Y_%m")
                months[key]["size"] += task.size if task.size else 0
                months[key]["task_list"].append(data)
            else:
                progress["size"] += task.size if task.size else 0
                progress["task_list"].append(data)

        return render(
            request,
            "simple_statistic.html",
            {
                "months": dict(months),
                "progress": progress,
            },
        )
