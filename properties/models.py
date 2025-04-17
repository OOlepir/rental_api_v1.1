from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User

class Property(models.Model):
    HOUSING_TYPES = [
        ('apartment', _('Квартира')),
        ('house', _('Дом')),
        ('studio', _('Студия')),
        ('loft', _('Лофт')),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(_('Заголовок'), max_length=255)
    description = models.TextField(_('Описание'))
    location = models.CharField(_('Местоположение'), max_length=255)
    price = models.DecimalField(_('Цена за ночь'), max_digits=10, decimal_places=2)
    rooms = models.PositiveSmallIntegerField(_('Количество комнат'))
    housing_type = models.CharField(_('Тип жилья'), max_length=20, choices=HOUSING_TYPES)
    is_active = models.BooleanField(_('Активно'), default=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
