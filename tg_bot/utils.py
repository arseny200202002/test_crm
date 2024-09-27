from .models import TgGroup

from .bot.utils import send_message


def notify_all_groups_about_event(event, details: dict):
    groups = TgGroup.objects.filter(send_notifications=True) # все группы, в которые будем писать
    for group in groups:
        msg = group.get_text_for_event(event, details) # получаем и форматируем текст сообщения
        if msg is not None:
            send_message(group.group_id, msg)
