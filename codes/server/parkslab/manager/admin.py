from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from manager import models as m


class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = m.UserAccount
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = m.UserAccount
        fields = ('email','name',)


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name',)}),
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
    list_display = ('id','name', 'email', 'last_login', 'up_date')
    list_filter = ('is_staff','is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('id',)


admin.site.register(m.UserAccount, MyUserAdmin)
admin.site.register(m.UserProfile)
admin.site.register(m.Project)
admin.site.register(m.ProjectStatusM)
admin.site.register(m.Organization)
admin.site.register(m.OrganizationDivM)
admin.site.register(m.OrganizationLight)
admin.site.register(m.CategoryM)
admin.site.register(m.BulletinBoard)
admin.site.register(m.BulletinBoardThread)
admin.site.register(m.BulletinBoardMessage)
