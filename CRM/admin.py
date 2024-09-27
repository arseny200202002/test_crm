from django.contrib import admin
from .models import (
    PlasticType, 
    Models3D,
    Order,
    Printer
)
from django.utils.safestring import mark_safe

@admin.register(PlasticType)
class PlasticTypeAdmin(admin.ModelAdmin):
    
    def link_url(self, obj):
        url = obj.link
        return mark_safe(f'<a target="_blank" href="{url}" rel="nofollow">Заказать</a>')
    link_url.short_description = 'Ссылка на товар'
    
    fields = ["manufacturer", "type", "color", "diameter", "wps", "price", "ppg", "link", "spools_in_stock", 'weight_in_stock']
    list_display = ["id", "manufacturer", "type", "color", "diameter", "wps", "price", "ppg", "link_url", 'spools_in_stock', 'weight_in_stock']
    readonly_fields = ['ppg']
    list_editable=[]

@admin.register(Models3D)
class Models3DAdmin(admin.ModelAdmin):
    
    def image_tag(self, obj):
        return mark_safe(f'<img src="{obj.photo.url}" width="150">')
    image_tag.short_description = 'Фото'
    
    def link_url(self, obj):
        self.verbose_name = 'obj._meta.verbose_name'
        url = obj.link
        site = obj.link.split('/')[2]
        return mark_safe(f'<a target="_blank" href="{url}" rel="nofollow">{site}</a>')
    link_url.short_description = 'Ссылка на модель'
    
    def marketplace_url(self, obj):
        url = obj.marketplace_link  
        return mark_safe(f'<a target="_blank" href="{url}" rel="nofollow">Маркетплейс</a>')
    marketplace_url.short_description = 'Ссылка на маркетплейс'
    
    def model_download(self, obj):
        return mark_safe('<a href="/media/{0}" download>.3mf</a>'.format(
            obj.file3mf))
    model_download.short_description = 'Скачать модель'
    
    def photo_download(self, obj):
        return mark_safe('<a href="/media/{0}" download>.zip</a>'.format(
            obj.file3mf))
    photo_download.short_description = 'Скачать архив'
    
    fields = ['name', 'plastic_type', 'link', 'file3mf', 'weight', 'manufacturing_price', 'revenue', 'price', 'test_print', 'photo', 'image_tag', 'zip_photo', 'marketplace_link']
    list_display = ['id', 'name', 'plastic_type', 'photo', 'link_url', 'model_download', 'weight', 'manufacturing_price', 'revenue', 'price', 'test_print', 'image_tag', 'photo_download', 'marketplace_url']
    readonly_fields = ['price', 'manufacturing_price', 'image_tag']
    list_editable=['photo','test_print']


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    fields=['name','diameter','price','lifetime','expences']
    list_display=['id','name','diameter','price','lifetime','expences','amortization']
    readonly_fields=[]
    list_editable=[]


@admin.register(Order)
class OrderrAdmin(admin.ModelAdmin):
    #def model_plastic_type(self, obj: Order):
    #    return obj.model.plastic_type
    #model_plastic_type.short_description = 'Тип пластика'

    fields=['model', 'quantity', 'printer']
    list_display=['id','model','quantity','printer','total_weight','manufacturing_price','total_price','plastic_in_stock','net_profit','wage']
    readonly_fields=[]
    list_editable=['printer','quantity']
