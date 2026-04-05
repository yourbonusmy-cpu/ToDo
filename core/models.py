import os
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

User = get_user_model()


class WeekdayChoices(models.IntegerChoices):
    MON = 0, "Понедельник"
    TUE = 1, "Вторник"
    WED = 2, "Среда"
    THU = 3, "Четверг"
    FRI = 4, "Пятница"
    SAT = 5, "Суббота"
    SUN = 6, "Воскресенье"


class MonthChoices(models.IntegerChoices):
    JAN = 1, "Январь"
    FEB = 2, "Февраль"
    MAR = 3, "Март"
    APR = 4, "Апрель"
    MAY = 5, "Май"
    JUN = 6, "Июнь"
    JUL = 7, "Июль"
    AUG = 8, "Август"
    SEP = 9, "Сентябрь"
    OCT = 10, "Октябрь"
    NOV = 11, "Ноябрь"
    DEC = 12, "Декабрь"


class PeriodType(models.TextChoices):
    NONE = "none", "Нет"
    DAY = "day", "День"
    WEEK = "week", "Неделя"
    MONTH = "month", "Месяц"
    YEAR = "year", "Год"


class ScheduleType(models.TextChoices):
    NONE = "none", "Нет"
    FLOATING = "floating", "В течение периода"
    FIXED = "fixed", "Не раньше даты"


def task_icon_upload_path(instance, filename):
    # instance.owner.username → имя пользователя
    # filename → оригинальное имя файла
    return os.path.join("image", instance.owner.username, "task_icons", filename)


class UserPin(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    pin_hash = models.CharField(max_length=128, blank=True, null=True)

    is_pin_enabled = models.BooleanField(default=False)

    def enable_pin(self, raw_pin: str | None = None):
        """
        Включить PIN.
        Если PIN не передан — установить 0000.
        """

        if raw_pin is None:
            raw_pin = "0000"

        self.pin_hash = make_password(raw_pin)
        self.is_pin_enabled = True
        self.save()

    def disable_pin(self):
        """
        Отключить PIN.
        PIN остаётся в базе.
        """
        self.is_pin_enabled = False
        self.save()

    def check_pin(self, raw_pin: str) -> bool:

        if not self.is_pin_enabled or not self.pin_hash:
            return False

        return check_password(raw_pin, self.pin_hash)


class SystemTaskTemplate(models.Model):

    code = models.CharField(max_length=64, unique=True)

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    is_hidden = models.BooleanField(default=False)

    icon = models.CharField(max_length=255, blank=True)

    default_amount = models.PositiveIntegerField(default=1)

    period_type = models.CharField(
        max_length=16, choices=PeriodType.choices, default=PeriodType.NONE
    )

    schedule_type = models.CharField(
        max_length=16, choices=ScheduleType.choices, default=ScheduleType.NONE
    )

    fixed_weekday = models.PositiveSmallIntegerField(
        choices=WeekdayChoices.choices, null=True, blank=True
    )

    fixed_day_of_month = models.PositiveSmallIntegerField(null=True, blank=True)

    fixed_month_of_year = models.PositiveSmallIntegerField(
        choices=MonthChoices.choices, null=True, blank=True
    )

    priority = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TaskTemplate(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    system_template = models.ForeignKey(
        SystemTaskTemplate, null=True, blank=True, on_delete=models.SET_NULL
    )
    is_hidden = models.BooleanField(default=False)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    icon = models.ImageField(
        upload_to=task_icon_upload_path, blank=True, null=True  # динамический путь
    )

    default_amount = models.PositiveIntegerField(default=1)

    period_type = models.CharField(
        max_length=16, choices=PeriodType.choices, default=PeriodType.NONE
    )
    schedule_type = models.CharField(
        max_length=16, choices=ScheduleType.choices, default=ScheduleType.NONE
    )

    # для задач по дням недели
    fixed_weekday = models.PositiveSmallIntegerField(
        choices=WeekdayChoices.choices, null=True, blank=True
    )

    # для задач по числу месяца
    fixed_day_of_month = models.PositiveSmallIntegerField(null=True, blank=True)

    # для задач раз в год
    fixed_month_of_year = models.PositiveSmallIntegerField(
        choices=MonthChoices.choices, null=True, blank=True
    )

    next_available_at = models.DateTimeField(null=True, blank=True)
    # когда шаблон последний раз использовали
    last_used_at = models.DateTimeField(null=True, blank=True)

    selected_count = models.PositiveIntegerField(default=0)
    priority = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):

        if self.schedule_type == ScheduleType.FIXED:

            if self.period_type == PeriodType.WEEK and not self.fixed_weekday:
                raise ValidationError("Нужно указать день недели")

            if self.period_type == PeriodType.MONTH and not self.fixed_day_of_month:
                raise ValidationError("Нужно указать день месяца")

            if self.period_type == PeriodType.YEAR and (
                not self.fixed_day_of_month or not self.fixed_month_of_year
            ):
                raise ValidationError("Нужно указать дату")

    class Meta:
        indexes = [
            models.Index(fields=["owner", "next_available_at"]),
            models.Index(fields=["owner", "priority"]),
            models.Index(fields=["owner", "selected_count"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["owner", "system_template"], name="unique_user_system_template"
            )
        ]


class GroupTemplate(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    tasks = models.ManyToManyField(TaskTemplate, related_name="group_templates")

    selected_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Block(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    priority = models.PositiveSmallIntegerField(default=0)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    target_date = models.DateField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-priority", "created_at"]


class BlockTask(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="tasks")
    template = models.ForeignKey(
        TaskTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="block_tasks",
    )
    title = models.CharField(max_length=128)
    icon = models.CharField(max_length=255, blank=True)
    is_hidden = models.BooleanField(default=False)
    is_encrypted = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    position = models.PositiveIntegerField()
    amount = models.PositiveIntegerField(default=1)
    time = models.FloatField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]
        indexes = [
            models.Index(fields=["block", "position"]),
        ]


class BlockWeather(models.Model):
    block = models.OneToOneField(
        Block, on_delete=models.CASCADE, related_name="weather"
    )

    city = models.CharField(max_length=64)

    data = models.JSONField()  # ← ВСЕ 4 периода сюда

    created_at = models.DateTimeField(auto_now_add=True)
