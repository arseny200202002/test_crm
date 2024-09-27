from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse

from tg_bot.models import Events
from tg_bot.utils import notify_all_groups_about_event

COLORS = (
    ("black", "черный"),
    ("red", "красный"),
    ("brown", "коричневый"),
    ("orange", "оранжевый"),
    ("white", "белый"),
    ("green", "зеленый"),
    ("blue", "синий"),
    ("crimson", "малиновый"),
    ("darkolivegreen", "оливковый"),
    ("cyan", "бирюзовый"),
    ("sliver", "серебристый"),
    ("gold", "золотоый"),
    ("aqua", "голубой"),
    ("purple", "фиолетовый"),
    ("beige", "бесцветный"),
)

SIZE = (
    (1.75, "1.75"),
    (2.85, "2.85"),
)


class PlasticType(models.Model):
    id = models.AutoField(primary_key=True)
    manufacturer = models.CharField(max_length=50, verbose_name="Производитель")
    link = models.URLField(default="https://rec3d.ru/", verbose_name="Ссылка на товар")
    type = models.CharField(max_length=50, verbose_name="Тип")
    color = models.CharField(choices=COLORS, max_length=50, verbose_name="Цвет")
    diameter = models.FloatField(choices=SIZE, verbose_name="Диаметр")
    wps = models.IntegerField(verbose_name="Вес катушки, г")
    price = models.IntegerField(verbose_name="Цена, руб.")
    spools_in_stock = models.IntegerField(default=0, verbose_name="Катушки в наличии")
    weight_in_stock = models.FloatField(default=0, verbose_name="Вес в наличии, г")

    def ppg(self):
        try:
            return float("{:.2f}".format(self.price / self.wps))
        except:
            return 0

    def __str__(self):
        return self.manufacturer + " " + self.type + " " + self.color + " " + str(self.diameter)

    class Meta:
        verbose_name = "Тип пластика"
        verbose_name_plural = "Типы пластика"


class Models3D(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="Название")
    plastic_type = models.ForeignKey(
        PlasticType, on_delete=models.CASCADE, verbose_name="Тип пластика"
    )
    link = models.URLField(verbose_name="Ссылка на модель")
    file3mf = models.FileField(upload_to="files/", verbose_name="Модель .3mf")
    weight = models.FloatField(verbose_name="Вес")

    def manufacturing_price(self):
        return float("{:.2f}".format(self.plastic_type.ppg() * self.weight))

    manufacturing_price.short_description = "Себес"

    revenue = models.FloatField(verbose_name="Маржинальность, %")

    def price(self):
        return float("{:.2f}".format(self.manufacturing_price() * self.revenue / 100))

    price.short_description = "Итоговая цена"

    test_print = models.BooleanField(default=False, verbose_name="Тестовая печать")
    photo = models.ImageField(default="logo.png", upload_to="photos/", verbose_name="Фото")
    zip_photo = models.FileField(
        blank=True, null=True, upload_to="photos/zip/", verbose_name="Архив с фото"
    )
    marketplace_link = models.URLField(default=None, blank=True, verbose_name="Маркетплейс")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Модель на печать"
        verbose_name_plural = "Модели на печать"


@receiver(pre_save, sender=Models3D)
def handle_pre_save(sender, instance: Models3D, **kwargs):
    """Ловит изменения в полях и отправляет уведомления"""
    obj = sender.objects.filter(pk=instance.pk).first()
    if obj is None:
        return
    link = reverse("admin:CRM_models3d_change", args=[instance.pk])
    if not obj.photo == instance.photo:  # Field has changed
        notify_all_groups_about_event(
            Events.photosAddedToModel,
            details={"admin_link": f"{settings.BASE_URL}{link}"},
        )
    if not obj.test_print == instance.test_print:  # Field has changed
        notify_all_groups_about_event(
            Events.testPrintStatusChanged,
            details={"admin_link": f"{settings.BASE_URL}{link}"},
        )


@receiver(post_save, sender=Models3D)
def handle_post_save(sender, instance: Models3D, created, **kwargs):
    """Ловит создание новой модели"""
    # на post save чтобы был pk
    if created:
        link = reverse("admin:CRM_models3d_change", args=[instance.pk])
        notify_all_groups_about_event(
            Events.modelAdded, details={"admin_link": f"{settings.BASE_URL}{link}"}
        )
