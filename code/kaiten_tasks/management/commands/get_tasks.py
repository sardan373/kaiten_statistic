from django.core.management.base import BaseCommand
from typing import Optional, Union

from kaiten_tasks.models import KaitenUser
from kaiten_tasks.workers.kaiten import KaitenWorker


class Command(BaseCommand):
    """
    Обновляет историю для переданного по kaiten_id пользователя.
    Алгоритм:
        - Актуализирует список пользователей - если пользователя с kaiten_id
        нет в базе.
        - Получает список всех задач пользователя с момента последнего
        обновления
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=int,
            help="id пользователя кайтена",
            default=193942,
        )
        # parser.add_argument("--postfix", type=str, default="", help="service_name_postfix")
        # parser.add_argument(
        #     "--last_check_dt",
        #     type=str,
        #     default="",
        #     help="последнее время создания претензии, которое проверены",
        # )
        # parser.add_argument(
        #     "--checks_periods",
        #     type=dict,
        #     default=dict(),
        #     help="плановые сроки решение заявки для типов, которые были в прошлый раз. Системное - не менять.",
        # )
        # parser.add_argument(
        #     "--queryset",
        #     type=dict,
        #     default=dict(),
        #     help="параметры фильтрации кверисета претензий",
        # )
        # parser.add_argument(
        #     "--sended_claims",
        #     type=list,
        #     default=list(),
        #     help="Проверенные в текущий запуск. Системное - не менять.",
        # )

    def _check_options(self, options: dict) -> None:
        if not options.get("user"):
            raise Exception("you must set --user option")

    def handle(self, *args, **options):
        self._check_options(options)

        self.worker = KaitenWorker()

        kaiten_user = self._get_user(options["user"])  # 193942
        if not kaiten_user:
            print("ERROR: user not found")
            return

        self.worker.update_tasks_for_user(kaiten_user)

        print("finish")

    def _get_user(self, kaiten_user_id: int) -> Optional[KaitenUser]:
        kaiten_user = KaitenUser.objects.filter(
            kaiten_id=kaiten_user_id
        ).first()
        if not kaiten_user:
            self.worker.update_users()
            kaiten_user = KaitenUser.objects.filter(
                kaiten_id=kaiten_user_id
            ).first()

        return kaiten_user
