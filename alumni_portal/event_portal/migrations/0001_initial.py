# Generated by Django 5.1.1 on 2024-10-22 04:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EventCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=225)),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("question", models.CharField(max_length=225)),
                ("options", models.CharField(blank=True, max_length=225, null=True)),
                ("help_text", models.CharField(blank=True, max_length=225, null=True)),
                ("is_faq", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("start_date", models.DateField()),
                ("start_time", models.TimeField()),
                ("venue", models.CharField(max_length=225)),
                ("address", models.TextField(blank=True, null=True)),
                ("link", models.URLField(blank=True, max_length=255, null=True)),
                ("is_public", models.BooleanField(default=True)),
                ("need_registration", models.BooleanField(default=True)),
                ("registration_close_date", models.DateField(blank=True, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "event_wallpaper",
                    models.ImageField(
                        blank=True, null=True, upload_to="events/wallpapers/"
                    ),
                ),
                ("instructions", models.TextField(blank=True, null=True)),
                ("posted_on", models.DateField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "posted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="event_portal.eventcategory",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EventComment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("comment_text", models.TextField()),
                ("commented_on", models.DateTimeField(auto_now_add=True)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="event_portal.event",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EventRegistration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("applied_on", models.DateField(auto_now_add=True)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="event_portal.event",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EventQuestion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="event_portal.event",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="event_portal.question",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RegistrationResponse",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("response", models.CharField(max_length=255)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="event_portal.question",
                    ),
                ),
                (
                    "registered_event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="event_portal.eventregistration",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EventLike",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("liked_on", models.DateTimeField(auto_now_add=True)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to="event_portal.event",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("event", "user")},
            },
        ),
    ]
