from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    # Пользователь, к которому привязана задача
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # Заголовок задачи
    title = models.CharField(max_length=200)
    # Описание задачи
    description = models.TextField(null=True, blank=True)
    # Флаг завершения задачи
    complete = models.BooleanField(default=False)
    # Дата и время создания задачи (устанавливается автоматически при создании)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-complete']
