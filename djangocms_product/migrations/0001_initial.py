# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal
import easy_thumbnails.fields
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')),
                ('first_name', models.CharField(max_length=50, verbose_name='Vorname')),
                ('last_name', models.CharField(max_length=50, verbose_name='Nachname')),
                ('address', models.CharField(max_length=150, verbose_name='Adresse')),
                ('zipcode', models.CharField(max_length=5, verbose_name='PLZ')),
                ('city', models.CharField(max_length=50, verbose_name='Ort')),
                ('country', models.CharField(default='', max_length=100, verbose_name='Land', blank=True)),
                ('telephone', models.CharField(max_length=50, verbose_name='Telefon')),
                ('email', models.EmailField(max_length=150, verbose_name='Email')),
                ('total_amount', models.DecimalField(default=Decimal('0.00'), verbose_name='Gesamtbetrag', max_digits=20, decimal_places=2)),
                ('shipping_amount', models.DecimalField(default=Decimal('0.00'), verbose_name='Versandkosten', max_digits=20, decimal_places=2)),
                ('shipping_label', models.CharField(default='', max_length=150, verbose_name='Versand-Label', blank=True)),
            ],
            options={
                'verbose_name': 'Bestellung',
                'verbose_name_plural': 'Bestellungen',
            },
        ),
        migrations.CreateModel(
            name='OrderedItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.PositiveIntegerField(default=0, verbose_name='Menge')),
                ('order', models.ForeignKey(verbose_name='Bestellung', to='djangocms_product.Order')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150, verbose_name='Titel')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Reihenfolge')),
                ('section', models.CharField(default='', max_length=50, verbose_name='Section', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug')),
                ('free_shipping', models.BooleanField(default=False, help_text='F\xfcr Produkte dieser Kategorie werden keine Versandkosten berechnet', verbose_name='Versandkostenfrei')),
            ],
            options={
                'verbose_name': 'Product Category',
                'verbose_name_plural': 'Product Categories',
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(upload_to=b'cms_product/', verbose_name='Bild')),
                ('image_width', models.PositiveSmallIntegerField(default=0, null=True, verbose_name='Breite des Originalbildes')),
                ('image_height', models.PositiveSmallIntegerField(default=0, null=True, verbose_name='H\xf6he des Originalbildes')),
                ('title', models.CharField(default=b'', max_length=150, verbose_name='Bild-Title', blank=True)),
                ('alt', models.CharField(default=b'', max_length=150, verbose_name='Alternativer Bild-Text', blank=True)),
                ('ordering', models.PositiveIntegerField(verbose_name='Sortierung')),
            ],
            options={
                'ordering': ['ordering'],
                'verbose_name': 'Product Image',
                'verbose_name_plural': 'Product Images',
            },
        ),
        migrations.CreateModel(
            name='ProductItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('changed_at', models.DateTimeField(auto_now=True, verbose_name='Created at')),
                ('active', models.BooleanField(default=False, verbose_name='Aktiv')),
                ('title', models.CharField(max_length=150, verbose_name='Headline of the product article')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug')),
                ('content', tinymce.models.HTMLField(verbose_name='Inhalt', blank=True)),
                ('price', models.DecimalField(default=Decimal('0.00'), verbose_name='Preis', max_digits=20, decimal_places=2)),
                ('special_offer', models.CharField(max_length=255, null=True, verbose_name='Special offer', blank=True)),
                ('document', models.FileField(upload_to=b'cms_products', null=True, verbose_name='Document (e.g. product catalogue, ...)', blank=True)),
                ('link', models.URLField(help_text='Link to more detailed page', null=True, verbose_name='Adresse (URL)', blank=True)),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Reihenfolge')),
                ('out_of_stock', models.BooleanField(default=False, verbose_name='ausverkauft')),
                ('product_categories', models.ManyToManyField(to='djangocms_product.ProductCategory', null=True, verbose_name='Selected product categories', blank=True)),
                ('target_page', models.ManyToManyField(to='cms.Page', null=True, verbose_name='Target Page', blank=True)),
            ],
            options={
                'ordering': ('-changed_at',),
                'verbose_name': 'Product Item',
                'verbose_name_plural': 'Product Items',
            },
        ),
        migrations.CreateModel(
            name='ProductTeaser',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(max_length=150, verbose_name='Headline of the product list')),
                ('ordering', models.CharField(default=b'past_desc', max_length=20, verbose_name='Ordering/Selection of Articles', choices=[(b'future_asc', 'from now to future (ascending)'), (b'past_desc', 'from now to past (descending)')])),
                ('product_categories', models.ManyToManyField(to='djangocms_product.ProductCategory', verbose_name='Selected product categories')),
                ('target_page', models.ForeignKey(verbose_name='Target Page', to='cms.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.AddField(
            model_name='productimage',
            name='product_item',
            field=models.ForeignKey(verbose_name='Product Item', to='djangocms_product.ProductItem'),
        ),
        migrations.AddField(
            model_name='ordereditem',
            name='product_item',
            field=models.ForeignKey(verbose_name='Bestelltes Produkt', to='djangocms_product.ProductItem'),
        ),
    ]
