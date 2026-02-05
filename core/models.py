from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cow(models.Model):
    cow_id = models.CharField(max_length=50, help_text="Identifier for the cow from ESP32 collar")
    temperature = models.FloatField(null=True, blank=True, help_text="Body temperature in Celsius")
    heart_rate = models.IntegerField(null=True, blank=True, help_text="Heart rate in BPM")
    activity_level = models.IntegerField(null=True, blank=True, help_text="Activity level (steps or movement count)")
    battery_level = models.FloatField(null=True, blank=True, help_text="Battery percentage (0-100)")
    latitude = models.FloatField(null=True, blank=True, help_text="GPS latitude coordinate")
    longitude = models.FloatField(null=True, blank=True, help_text="GPS longitude coordinate")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When the data was received")
    raw_data = models.JSONField(null=True, blank=True, help_text="Original JSON data received from ESP32")

    def __str__(self):
        return f"Cow {self.cow_id}"
