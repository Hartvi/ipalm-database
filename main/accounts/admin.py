from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .forms import UserRegisterForm
# from .models import CustomUser

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = UserRegisterForm
    # form = UserChangeForm
    model = User
    list_display = ('username', 'organization', 'email', 'is_staff', 'is_active',)
    list_filter = ('username', 'organization', 'email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'organization', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'organization', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('username', 'organization', 'email',)
    ordering = ('username', 'organization', 'email',)


admin.site.register(User, CustomUserAdmin)
