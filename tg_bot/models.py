from typing import Optional

from django.db import models


class Events(models.TextChoices):
    modelAdded = "3dModelAdded", "Добавлена новая модель"
    orderAdded = "OrderAdded", "Создан новый заказ"
    photosAddedToModel = "photosAddedToModel", "Добавлены фото к модели"
    testPrintStatusChanged = "testPrintStatusChanged", "Статус тестовой печати изменен"


class TgGroup(models.Model):
    id = models.AutoField(primary_key=True)
    group_id = models.IntegerField(verbose_name="ID группы")
    group_name = models.CharField(max_length=255, verbose_name="Название группы")
    send_notifications = models.BooleanField(default=False, verbose_name="Отправлять уведомления")
    handle_messages = models.BooleanField(default=False, verbose_name="Обрабатывать сообщения")

    def __str__(self):
        return self.group_name

    def get_text_for_event(self, event, details: Optional[dict] = None) -> Optional[str]:
        """Получить текст сообщения для события"""
        msg = self.tgmessagetext_set.filter(event=event).first()  # type: ignore
        if not msg:
            return None
        if not details:
            return msg.text
        return msg.text.format(**details)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class TgMessageText(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(TgGroup, on_delete=models.CASCADE, verbose_name="Группа")
    event = models.CharField(
        max_length=255,
        verbose_name="Событие",
        choices=Events.choices,
    )
    text = models.TextField(verbose_name="Текст сообщения")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Текст сообщения"
        verbose_name_plural = "Тексты сообщений"
        unique_together = (
            "group",
            "event",
        )
