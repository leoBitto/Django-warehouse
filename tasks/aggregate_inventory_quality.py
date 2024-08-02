import logging
from django.db.models import Count
from django.utils import timezone
from django.db import transaction
from gold_bi.models import InventoryQualityAggregation
from inventory.models import Product

logger = logging.getLogger('gold_bi')

def aggregate_inventory_quality():
    try:
        # Ottieni la data corrente
        now = timezone.now()
        month = now.month
        year = now.year

        # Aggregazione della qualità dei dati
        products_missing_category = Product.objects.using('default').filter(category__isnull=True).count()
        products_missing_image = Product.objects.using('default').filter(image__isnull=True).count()
        products_missing_description = Product.objects.using('default').filter(description__isnull=True).count()
        products_missing_both = Product.objects.using('default').filter(image__isnull=True, description__isnull=True).count()

        # Creazione del dizionario per l'aggregazione
        quality_aggregations = {
            'products_missing_category': products_missing_category,
            'products_missing_image': products_missing_image,
            'products_missing_description': products_missing_description,
            'products_missing_both': products_missing_both,
        }

        # Aggiornamento o creazione del record nel modello InventoryQualityAggregation
        with transaction.atomic(using='gold'):
            obj, created = InventoryQualityAggregation.objects.using('gold').get_or_create(
                month=month,
                year=year
            )
            
            # Aggiorna i campi con i valori aggregati
            for field, value in quality_aggregations.items():
                setattr(obj, field, value)
            obj.save()

        logger.info(f'Inventory quality aggregation for {month}/{year} completed successfully.')
    except Exception as e:
        logger.error(f'Error in inventory quality aggregation for {month}/{year}: {e}')
