from apps.users.forms import CustomUserCreationForm, GroupAdminForm
from apps.users.models import User
from apps.users.services.user import UserService
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group


def resend_verification_email(modeladmin, request, queryset):
    for user in queryset:
        if not user.is_email_active:
            UserService().send_email_activation_code(user)


resend_verification_email.short_description = "Resend verification email to user"


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User
    add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    list_display = (
        'pk',
        'first_name',
        'last_name',
        'registration_date',
        'email',
        'is_email_active',
        'is_superuser',
        'is_staff',
    )
    list_filter = (
        'is_email_active',
        'is_staff',
        'is_superuser',
    )

    fieldsets = (
        ('Information', {'fields': (
            'first_name',
            'last_name',
            'email',
            'password',
            'avatar',
            )}),
        ('Status', {'fields': ('is_active', 'is_email_active', 'status',)}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')},
         ),
        ('Information', {'fields': ('first_name', 'last_name', 'avatar',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active',)}),
    )
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    actions = [resend_verification_email]

    def registration_date(self, obj):
        return obj.created_at.strftime("%d.%m.%Y")


class UserInfo(User):
    class Meta:
        proxy = True
        verbose_name = 'Users Statistics'
        app_label = 'users'  # or another app to put your custom view


admin.site.unregister(Group)


class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    filter_horizontal = ['permissions']


admin.site.register(Group, GroupAdmin)
