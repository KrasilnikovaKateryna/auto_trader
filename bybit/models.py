from django.db import models


class Trader(models.Model):
    username = models.CharField(max_length=10)
    api_key = models.CharField(max_length=30)
    api_secret = models.CharField(max_length=45)
    balance = models.DecimalField(decimal_places=2, max_digits=8)

    def __str__(self):
        return f"Username {self.username}"


class Settings(models.Model):
    stop_loss_percent = models.FloatField()
    leverage = models.FloatField()
    amount_usd = models.FloatField()
    stop_loss_step = models.FloatField()
    demo = models.BooleanField(default=False)

    def __str__(self):
        return f"Setting {self.id}"

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"


class Chat(models.Model):
    name = models.CharField(max_length=80)
    chat_id = models.CharField(max_length=80)

    def __str__(self):
        return f"Chat {self.name}"


class EntryPrice(models.Model):
    symbol = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()


class ErrorLog(models.Model):
    error = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

