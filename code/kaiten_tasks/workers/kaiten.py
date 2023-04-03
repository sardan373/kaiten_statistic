import json
import pytz
from datetime import datetime

from django.utils.timezone import utc

from kaiten_tasks.models import KaitenTask, KaitenUser
from kaiten_tasks.workers.api import ApiClient


class KaitenWorker:
    PROGRESS_ID = 284916
    REVIEW_ID = 284917

    def __init__(self):
        self.client = ApiClient()

    def update_users(self) -> None:
        kaiten_users_list = self.client.users()
        KaitenUser.objects.bulk_create(
            [
                KaitenUser(
                    kaiten_id=user["id"],
                    name=user["full_name"],
                    email=user["email"],
                    active=True,
                )
                for user in kaiten_users_list
            ],
            update_conflicts=True,
            unique_fields=["kaiten_id"],
            update_fields=["name", "email", "active"],
        )
        KaitenUser.objects.exclude(
            kaiten_id__in=[user["id"] for user in kaiten_users_list]
        ).update(active=False)

    def update_tasks_for_user(self, kaiten_user: KaitenUser) -> dict:
        current_time = datetime.utcnow().replace(tzinfo=utc)

        tasks_ids_list = self.update_tasks(kaiten_user)

        print(f"total tasks to update: {len(tasks_ids_list)}")
        updated_count = 0
        for task_id in tasks_ids_list:
            self.update_task_history(task_id, kaiten_user.last_sync, current_time)
            updated_count += 1
            if updated_count % 10 == 0:
                print(f"updated_count {updated_count}")
        
        kaiten_user.last_sync = current_time
        kaiten_user.save()

    def update_tasks(self, kaiten_user: KaitenUser) -> None:
        tasks_list = self.client.tasks_for_user(
            kaiten_user.kaiten_id,
            last_sync=kaiten_user.last_sync,
        )

        tasks_objs = {
            task["id"]:
            KaitenTask(
                kaiten_id=task["id"],
                name=task["title"],
                user=kaiten_user,
                size=task["size"],
                created=task["created"],
                updated=task["updated"],
            ) for task in tasks_list
        }

        if tasks_objs:
            KaitenTask.objects.bulk_create(
                tasks_objs.values(),
                update_conflicts=True,
                unique_fields=["kaiten_id"],
                update_fields=["name", "user", "size", "updated"],
            )

        return tasks_objs.keys()

    def update_task_history(self, card_id: int, user_last_sync: datetime, current_time: datetime) -> None:
        card = KaitenTask.objects.get(kaiten_id=card_id)

        # Если мы уже обновляли, но упали по каким-то причинам, пропускаем эту
        # карточку - получим обновление в следующие раз
        if card.last_sync and (not user_last_sync or card.last_sync > user_last_sync):
            return

        time_logs = self.client.get_activities(card_id)
        in_progress = None
        in_review = None
        for action in time_logs:
            if action["action"] == "card_move":
                action_time = datetime.fromisoformat(action["created"])
                column_id = action["column"]["id"]
                if (
                    column_id == self.PROGRESS_ID
                    and (not in_progress or in_progress > action_time)
                ):
                    in_progress = action_time
                if (
                    column_id == self.REVIEW_ID
                    and (not in_review or in_review > action_time)
                ):
                    in_review = action_time
        if in_progress or in_review:
            card.moved_to_progress = in_progress
            card.moved_to_review = in_review
            card.last_sync = current_time
            card.save()
