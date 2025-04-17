from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import User
from properties.models import Property


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Ожидает подтверждения')),
        ('confirmed', _('Подтверждено')),
        ('rejected', _('Отклонено')),
        ('canceled', _('Отменено')),
        ('completed', _('Завершено')),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField(_('Дата заезда'))
    check_out_date = models.DateField(_('Дата выезда'))
    guests_count = models.PositiveSmallIntegerField(_('Количество гостей'), default=1)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.check_out_date <= self.check_in_date:
            raise ValidationError(_('Дата выезда должна быть позже даты заезда'))
        if self.check_in_date < timezone.now().date():
            raise ValidationError(_('Дата заезда не может быть в прошлом'))
        overlaps = Booking.objects.filter(
            property=self.property,
            status__in=['pending', 'confirmed'],
            check_in_date__lt=self.check_out_date,
            check_out_date__gt=self.check_in_date,
        )
        if self.pk:
            overlaps = overlaps.exclude(pk=self.pk)
        if overlaps.exists():
            raise ValidationError(_('Выбранные даты уже заняты'))

    def calculate_total_price(self):
        days = (self.check_out_date - self.check_in_date).days
        self.total_price = days * self.property.price

    def save(self, *args, **kwargs):
        self.clean()
        self.calculate_total_price()
        super().save(*args, **kwargs)
