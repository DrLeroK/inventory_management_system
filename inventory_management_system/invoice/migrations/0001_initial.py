# Generated by Django 4.2.19 on 2025-04-23 15:49

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', django_extensions.db.fields.AutoSlugField(blank=True, editable=False, help_text='Auto-generated URL identifier', populate_from='date', unique=True)),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Invoice Date')),
                ('customer_name', models.CharField(max_length=100, verbose_name='Customer Name')),
                ('contact_number', models.CharField(max_length=15, verbose_name='Contact Number')),
                ('price_per_item', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Price Per Item (Ksh)')),
                ('quantity', models.DecimalField(decimal_places=2, default=1.0, max_digits=10, verbose_name='Quantity')),
                ('shipping', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Shipping Cost (Ksh)')),
                ('total', models.DecimalField(decimal_places=2, editable=False, max_digits=10, verbose_name='Subtotal (Ksh)')),
                ('grand_total', models.DecimalField(decimal_places=2, editable=False, max_digits=10, verbose_name='Total Amount (Ksh)')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.item', verbose_name='Purchased Item')),
            ],
            options={
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices',
                'ordering': ['-date'],
            },
        ),
    ]
