from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import UserAccount, Project, CategoryM


class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = UserAccount
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = UserAccount
        fields = ('email','name','display_name','birthday',)


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name', 'display_name', 'birthday')}),
        (_('Permissions'), {'fields': ('is_active', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'up_date')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('name', 'email', 'last_login', 'up_date')
    list_filter = ('is_staff','is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'name', 'birthday')
    ordering = ('name',)


admin.site.register(UserAccount, MyUserAdmin)
admin.site.register(Project)
admin.site.register(CategoryM)
