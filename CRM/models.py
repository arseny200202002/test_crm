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


class BaseModel(models.Model):
    id=models.AutoField(primary_key=True)
    class Meta:
        abstract=True

class PlasticType(BaseModel):
    manufacturer = models.CharField(max_length=50, verbose_name="Производитель")
    link = models.URLField(default="https://rec3d.ru/", verbose_name="Ссылка на товар")
    type = models.CharField(max_length=50, verbose_name="Тип")
    color = models.CharField(choices=COLORS, max_length=50, verbose_name="Цвет")
    diameter = models.FloatField(choices=SIZE, verbose_name="Диаметр, мм")
    wps = models.IntegerField(verbose_name="Вес катушки, г")
    price = models.IntegerField(verbose_name="Цена, руб.")
    spools_in_stock = models.IntegerField(default=0, verbose_name="Катушки в наличии, шт")
    weight_in_stock = models.FloatField(default=0, verbose_name="Вес в наличии, г")


    def ppg(self):
        try:
            return float("{:.2f}".format(self.price / self.wps))
        except: return 0
    ppg.short_description = "Цена за грамм"

    def __str__(self):
        return self.manufacturer + " " + self.type + " " + self.color + " " + str(self.diameter)

    class Meta:
        verbose_name = "Тип пластика"
        verbose_name_plural = "Типы пластика"


class Models3D(BaseModel):
    name = models.CharField(max_length=50, verbose_name="Название")
    plastic_type = models.ForeignKey(PlasticType, on_delete=models.CASCADE, verbose_name="Тип пластика")
    link = models.URLField(verbose_name="Ссылка на модель")
    file3mf = models.FileField(upload_to="files/", verbose_name="Модель .3mf")
    weight = models.FloatField(verbose_name="Вес, г")
    revenue = models.FloatField(verbose_name="Наценка, %")
    test_print = models.BooleanField(default=False, verbose_name="Тестовая печать")
    photo = models.ImageField(default="logo.png", upload_to="photos/", verbose_name="Фото")
    zip_photo = models.FileField(blank=True, null=True, upload_to="photos/zip/", verbose_name="Архив с фото")
    marketplace_link = models.URLField(default=None, blank=True, verbose_name="Маркетплейс")

    def manufacturing_price(self):
        return float("{:.2f}".format(self.plastic_type.ppg() * self.weight))
    manufacturing_price.short_description = "Себесстоимость, руб."


    def price(self):
        return float("{:.2f}".format(self.manufacturing_price() * (1 + self.revenue/100)))
    price.short_description = "Итоговая цена, руб."

    def time_to_print(self):
        return 7
    time_to_print.short_description="Время печати, часов"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Модель на печать"
        verbose_name_plural = "Модели на печать"


class Printer(BaseModel):
    name=models.CharField(max_length=256, verbose_name="Модель принтера")
    diameter=models.FloatField(choices=SIZE, verbose_name="Диаметр, мм")   
    price=models.IntegerField(verbose_name="Цена, руб.")
    lifetime=models.IntegerField(verbose_name="Срок жизни, лет")
    expences=models.IntegerField(verbose_name="Стоимость часа работы, руб.")

    # Смысл имеет лишь величина: стоимость часа работы
    def amortization(self):
        return int(self.price / self.lifetime / 365 / 24 + self.expences)
    amortization.short_description="Амортизация, руб/час"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Принтер"
        verbose_name_plural="Принтеры"

class Order(BaseModel):
    model=models.ForeignKey(to=Models3D, on_delete=models.CASCADE, verbose_name="Модель")
    quantity=models.IntegerField(verbose_name="Количество", default=1)
    printer=models.ForeignKey(to=Printer, on_delete=models.CASCADE, verbose_name="Принтер", related_name="orders")


    def total_weight(self):
        return int(self.model.weight * self.quantity)
    total_weight.short_description="Общий вес, г"

    def manufacturing_price(self):
        return float("{:.2f}".format(self.quantity * (self.model.manufacturing_price() + self.printer.amortization() * self.model.time_to_print())))
    manufacturing_price.short_description="Цена производства, руб."

    def total_price(self):
        return float("{:.2f}".format(self.quantity * (self.model.price() + self.printer.amortization() * self.model.time_to_print())))
    total_price.short_description="Общая цена, руб."

    def plastic_in_stock(self):
        return bool(self.model.plastic_type.weight_in_stock > 0)
    plastic_in_stock.short_description="Пластик в наличии"

    def net_profit(self):
        return float("{:.2f}".format((self.total_price() - self.manufacturing_price()) * 0.7))
    net_profit.short_description="Чистая прибыль, руб."

    def wage(self):
        return float("{:.2f}".format((self.total_price() - self.manufacturing_price()) * 0.3))
    wage.short_description="Оплата труда, руб."

    def __str__(self):
        return f"Принтер: {self.printer.name}, модель: {self.model.name}" 

    class Meta:
        verbose_name="Заказ на печать"
        verbose_name_plural="Заказы на печать"




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
        print('photo field has changed')
    if not obj.test_print == instance.test_print:  # Field has changed
        notify_all_groups_about_event(
            Events.testPrintStatusChanged,
            details={"admin_link": f"{settings.BASE_URL}{link}"},
        )
        print('test_print field has changed')


@receiver(post_save, sender=Models3D)
def handle_post_save(sender, instance: Models3D, created, **kwargs):
    """Ловит создание новой модели"""
    # на post save чтобы был pk
    if created:
        link = reverse("admin:CRM_models3d_change", args=[instance.pk])
        notify_all_groups_about_event(
            Events.modelAdded, details={"admin_link": f"{settings.BASE_URL}{link}"}
        )
