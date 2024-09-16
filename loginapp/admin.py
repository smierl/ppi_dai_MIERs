from django.contrib import admin
from .models import Gym, User
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')