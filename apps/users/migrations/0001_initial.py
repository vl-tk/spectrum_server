# Generated by Django 3.2.14 on 2022-09-06 14:29

from django.conf import settings
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.CharField(error_messages={'unique': 'A user with that email already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator(), django.core.validators.EmailValidator()], verbose_name='Email')),
                ('first_name', models.CharField(blank=True, max_length=30, null=True, validators=[django.core.validators.MinLengthValidator(0)], verbose_name='First name')),
                ('last_name', models.CharField(blank=True, max_length=30, null=True, validators=[django.core.validators.MinLengthValidator(0)], verbose_name='Last name')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Active'), (1, 'Baned')], default=0, verbose_name='Status')),
                ('password', models.CharField(max_length=254, verbose_name='Password')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='Is active')),
                ('is_email_active', models.BooleanField(default=False, verbose_name='Email confirmed')),
                ('activation_email_code', models.CharField(blank=True, max_length=32, null=True, verbose_name='Email confirmation code')),
                ('email_activation_date', models.DateTimeField(blank=True, null=True)),
                ('reset_password_code', models.CharField(blank=True, max_length=32, null=True, verbose_name='Password reset code')),
                ('reset_password_code_expire', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OutstandingToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jti', models.CharField(max_length=255, unique=True)),
                ('token', models.TextField()),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user',),
            },
        ),
        migrations.CreateModel(
            name='BlacklistedToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blacklisted_at', models.DateTimeField(auto_now_add=True)),
                ('token', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.outstandingtoken')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
            ],
            options={
                'verbose_name': 'Users Statistics',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('users.user',),
        ),
    ]
