from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories'
    )
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='categories/icons/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name


class CommissionRule(models.Model):
    class CommissionType(models.TextChoices):
        PERCENTAGE = 'PERCENTAGE', _('Percentage')
        FLAT = 'FLAT', _('Flat Fee')

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='commission_rules')
    commission_type = models.CharField(
        max_length=20, choices=CommissionType.choices, default=CommissionType.PERCENTAGE
    )
    commission_value = models.DecimalField(max_digits=6, decimal_places=2, help_text="e.g. 10.00 for 10%")
    minimum_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    maximum_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    priority = models.IntegerField(default=0, help_text="Higher priority rule applies first")
    effective_from = models.DateTimeField(null=True, blank=True)
    effective_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Commission Rule')
        verbose_name_plural = _('Commission Rules')
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.category.name} - {self.commission_value}% (Priority {self.priority})"
