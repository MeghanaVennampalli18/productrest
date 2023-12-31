# Generated by Django 4.2.3 on 2023-08-11 04:14

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminDetails',
            fields=[
                ('admin_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator(message='Usertype must be a string.', regex='^[a-zA-Z]+$')])),
                ('password', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator(message='Usertype must be a string.', regex='^[a-zA-Z]+$')])),
                ('category', models.CharField(max_length=100)),
                ('brand', models.CharField(max_length=50)),
                ('price', models.IntegerField()),
                ('description', models.CharField(max_length=300)),
                ('image', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='UserDetails',
            fields=[
                ('user_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator(message='Usertype must be a string.', regex='^[a-zA-Z]+$')])),
                ('password', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('cart_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('quantity', models.IntegerField(default=1)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productrest.product')),
            ],
        ),
    ]
