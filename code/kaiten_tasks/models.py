from django.db import models


class KaitenUser(models.Model):
    kaiten_id = models.IntegerField(
        verbose_name="Id кайтена", db_index=True, unique=True
    )
    name = models.CharField(verbose_name="Имя", max_length=512)
    email = models.CharField(verbose_name="Email", max_length=512)
    active = models.BooleanField(
        verbose_name="Присутствует в kaiten",
        default=True,
        help_text="Присутствовал ли пользователь в выгрузке из kaiten",
    )
    last_sync = models.DateTimeField(
        verbose_name="Последняя синхронизация", null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Пользователи"
        verbose_name = "Пользователь"

    def __str__(self):
        return self.name


class KaitenTask(models.Model):
    kaiten_id = models.IntegerField(
        verbose_name="Id кайтена", db_index=True, unique=True
    )
    name = models.CharField(
        max_length=1024, verbose_name="Название", db_index=True
    )
    user = models.ForeignKey(
        KaitenUser,
        verbose_name="Пользователь kaiten",
        on_delete=models.PROTECT,
    )
    size = models.IntegerField(verbose_name="Размер", null=True, blank=True)
    created = models.DateTimeField(
        verbose_name="Время создания", help_text="в kaiten"
    )
    updated = models.DateTimeField(
        verbose_name="Время обновления", help_text="в kaiten"
    )
    moved_to_progress = models.DateTimeField(
        verbose_name="Перемещена в работу",
        null=True,
        blank=True,
    )
    moved_to_review = models.DateTimeField(
        verbose_name="Перемещена в ревью",
        help_text="первый раз",
        null=True,
        blank=True,
    )
    last_sync = models.DateTimeField(
        verbose_name="Последнее получение истории задачи",
        help_text="служебное поле",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Задачи"
        verbose_name = "Задача"

    def __str__(self):
        return self.name
