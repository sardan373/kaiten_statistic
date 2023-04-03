import time
from datetime import datetime
from typing import Optional, Union

from django.conf import settings

import requests
from requests.exceptions import JSONDecodeError
from requests.models import Response


class ApiClient:
    api_url = None
    headers = {}
    reset_at = 0

    def __init__(self, headers: dict = {}):
        self.api_url = "https://life-pay.kaiten.ru/api/v1"
        self.headers = {"Authorization": f"Bearer {settings.KAITEN_TOKEN}"}
        self.headers.update(headers)

    def _control_calls(self, result: Response) -> None:
        # kaiten в заголовке X-RateLimit-Remaining отдает сколько вызовов
        # осталось до окончания лимита, в заголовке X-RateLimit-Reset - когда
        # лимит будет сброшен
        calls_remaining = result.headers.get("X-RateLimit-Remaining")
        calls_reset_timestamp = result.headers.get("X-RateLimit-Reset")
        if (
            calls_remaining is not None
            and calls_reset_timestamp is not None
            and int(calls_remaining) == 0
        ):
            self.reset_at = int(calls_reset_timestamp)

    def _sleep_if_needed(self) -> None:
        now_ts = int(datetime.now().timestamp())
        if now_ts < self.reset_at:
            time.sleep(self.reset_at - now_ts)

    def _send(
        self, method: str, url: str, data: dict = {}
    ) -> Union[list, dict]:
        print(f"SEND CALL TO KAITEN: {url}")
        self._sleep_if_needed()
        params = {
            "params" if method == "get" else "data": data,
            "headers": self.headers,
        }
        result = getattr(requests, method)(
            f"{self.api_url}/{url}",
            **params,
        )
        self._control_calls(result)
        if result.status_code != 200:
            raise Exception(
                f"UNSUCCESS CALL for {url}: "
                f"{result.status_code} | {result.content}"
            )

        try:
            jsoned = result.json()
        except JSONDecodeError:
            raise Exception(
                f"ERROR for {url}: {result.status_code} | {result.content}"
            )
        return jsoned

    def _call_with_limits(
        self,
        method: str,
        url: str,
        data: dict = {},
        limit: int = None,
    ) -> Union[list, dict]:
        # TODO: замутить генератор
        if limit:
            result = []
            page = 0
            while True:
                if page:
                    data["offset"] = page * limit
                    data["limit"] = limit
                send_result = self._send(method, url, data)
                result.extend(send_result)

                if not limit or len(send_result) < limit or page > 1:
                    break

                page += 1
        else:
            result = self._send(method, url, data)

        return result

    def post(
        self, url: str, data: dict = {}, limit: Optional[int] = None
    ) -> Union[list, dict]:
        return self._call_with_limits("post", url, data, limit)

    def get(
        self, url: str, data: dict = {}, limit: Optional[int] = None
    ) -> Union[list, dict]:
        return self._call_with_limits("get", url, data, limit)

    def users(self) -> list:
        return self.get("users")

    def tasks_for_user(
        self,
        kaiten_user_id: Union[int, str],
        last_sync: Optional[datetime],
    ) -> list:
        data = {"responsible_ids": kaiten_user_id}
        if last_sync:
            data["updated_after"] = last_sync.isoformat()
        return self.get(
            "cards",
            data=data,
            limit=100,
        )

    def task(self, card_id: Union[int, str]) -> dict:
        return self.get(f"cards/{card_id}")

    def get_activities(self, card_id: Union[int, str]) -> dict:
        # не документировано - подсмотрел запрос в запросе на историю
        # карточки в браузере :(
        return self.get(f"cards/{card_id}/activity?with_timeline_fields=false")
