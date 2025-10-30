from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import datetime
import json

from apps.inventory.models.category import Category
from apps.inventory.models.unit_of_mesure import UnitOfMesure
from apps.inventory.models.product_type import ProductType
from apps.inventory.models.location_type import LocationType
from apps.inventory.models.stock_location import StockLocation
from apps.inventory.models.operation_type import OperationType
from apps.inventory.models.product import Product
from apps.inventory.models.product_location import ProductLocation

data = [
    {"model": "inventory.category", "pk": 2, "fields": {"label": "amoxil", "description": "amoxilciline"}}, {"model": "inventory.category", "pk": 4, "fields": {"label": "légumes", "description": "nourriture"}}, {"model": "inventory.category", "pk": 5, "fields": {"label": "Fourniture", "description": "fourniture des bureaux"}}, {"model": "inventory.category", "pk": 6, "fields": {"label": "équipement", "description": "les Equipment"}}, {"model": "inventory.category", "pk": 7, "fields": {"label": "boissons", "description": "boissons a boire"}}, {"model": "inventory.unitofmesure", "pk": 3, "fields": {"label": "Litre", "symbole": "L"}}, {"model": "inventory.unitofmesure", "pk": 4, "fields": {"label": "Gramme", "symbole": "g"}}, {"model": "inventory.unitofmesure", "pk": 6, "fields": {"label": "piéces", "symbole": "pcs"}}, {"model": "inventory.unitofmesure", "pk": 7, "fields": {"label": "paquets", "symbole": "pqt"}}, {"model": "inventory.product", "pk": 23, "fields": {"name": "Tomates", "default_code": "PDT-0001", "barcode": "23456778", "standard_price": "8.00", "description": "tomates", "active": True, "image_1920": "", "weight": 10.0, "volume": 5.0, "dlc": "2025-08-17", "stock_minimal": 30, "categ": 4, "uom": 4, "product_type": 1, "total_quantity_cached": "20.00"}}, {"model": "inventory.product", "pk": 24, "fields": {"name": "Stylo BIC", "default_code": "PDT-0002", "barcode": "765435678", "standard_price": "2.00", "description": "stylo d ecriture", "active": True, "image_1920": "", "weight": 10.0, "volume": 10.0, "dlc": "2025-08-17", "stock_minimal": 20, "categ": 6, "uom": 6, "product_type": 1, "total_quantity_cached": "80.00"}}, {"model": "inventory.product", "pk": 25, "fields": {"name": "Table", "default_code": "PDT-0003", "barcode": "765432456", "standard_price": "1000.00", "description": "table a manger", "active": True, "image_1920": "", "weight": 1000.0, "volume": 3000.0, "dlc": "2025-08-17", "stock_minimal": 15, "categ": 5, "uom": 6, "product_type": 1, "total_quantity_cached": "100.00"}}, {"model": "inventory.product", "pk": 26, "fields": {"name": "Pomme de terre", "default_code": "PDT-0004", "barcode": "87654324567", "standard_price": "100.00", "description": "pomme de terre", "active": True, "image_1920": "", "weight": 10.0, "volume": 20.0, "dlc": "2025-08-17", "stock_minimal": 10, "categ": 4, "uom": 4, "product_type": 1, "total_quantity_cached": "20.00"}}, {"model": "inventory.product", "pk": 27, "fields": {"name": "Eau miniral", "default_code": "PDT-0005", "barcode": "9876543245678", "standard_price": "200.00", "description": "eau miniral pour les medicaments", "active": True, "image_1920": "", "weight": 20.0, "volume": 30.0, "dlc": "2025-08-17", "stock_minimal": 20, "categ": 7, "uom": 3, "product_type": 1, "total_quantity_cached": "200.00"}}, {"model": "inventory.stocklocation", "pk": 7, "fields": {"name": "EMP 1", "parent_location": None, "location_type": 1}}, {"model": "inventory.stocklocation", "pk": 8, "fields": {"name": "EMP 2", "parent_location": None, "location_type": 1}}, {"model": "inventory.stocklocation", "pk": 9, "fields": {"name": "EMP 3", "parent_location": None, "location_type": 1}}, {"model": "inventory.stocklocation", "pk": 10, "fields": {"name": "EMP 4", "parent_location": None, "location_type": 1}}, {"model": "inventory.stocklocation", "pk": 11, "fields": {"name": "EMP 5", "parent_location": None, "location_type": 1}}, {"model": "inventory.stocklocation", "pk": 12, "fields": {"name": "EMP 6", "parent_location": None, "location_type": 1}}, {"model": "inventory.locationtype", "pk": 1, "fields": {"label": "type emplcemnt 1", "description": "description emplacemnt 1"}}, {"model": "inventory.producttype", "pk": 1, "fields": {"label": "stockable"}}, {"model": "inventory.producttype", "pk": 3, "fields": {"label": "effervescent"}}, {"model": "inventory.operationtype", "pk": 1, "fields": {"label": "Transfert interne"}}, {"model": "inventory.operationtype", "pk": 2, "fields": {"label": "Consommation"}}, {"model": "inventory.operationtype", "pk": 3, "fields": {"label": "Réception"}}, {"model": "inventory.productlocation", "pk": 26, "fields": {"product": 23, "location": 7, "quantity_stored": "10.00", "last_count_date": "2025-08-17", "quantity_counted": "0.00"}}, {"model": "inventory.productlocation", "pk": 27, "fields": {"product": 23, "location": 8, "quantity_stored": "10.00", "last_count_date": "2025-08-17", "quantity_counted": "0.00"}}, {"model": "inventory.productlocation", "pk": 28, "fields": {"product": 24, "location": 9, "quantity_stored": "50.00", "last_count_date": "2025-08-17", "quantity_counted": "0.00"}}, {"model": "inventory.productlocation", "pk": 29, "fields": {"product": 24, "location": 10, "quantity_stored": "30.00", "last_count_date": "2025-08-17", "quantity_counted": "0.00"}}, {"model": "inventory.productlocation", "pk": 30, "fields": {"product": 25, "location": 11, "quantity_stored": "100.00", "last_count_date": "2025-08-17", "quantity_counted": "0.00"}}, {"model": "inventory.productlocation", "pk": 31, "fields": {"product": 26, "location": 12, "quantity_stored": "20.00", "last_count_date": "2025-08-17", "quantity_counted": "0.00"}}, {"model": "inventory.productlocation", "pk": 32, "fields": {"product": 27, "location": 12, "quantity_stored": "100.00", "last_count_date": "2025-08-17", "quantity_counted": "0.00"}}, {"model": "inventory.productlocation", "pk": 33, "fields": {"product": 27, "location": 11, "quantity_stored": "100.00", "last_count_date": "2025-08-17", "quantity_counted": "0.00"}}
    ]


def parse_date(date_str: str):
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    return None


class Command(BaseCommand):
    help = "Insère les données dumpdata pour l'app inventory (catégories, produits, etc.)"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            nargs="?",
            help="Chemin optionnel vers le fichier JSON exporté via `python manage.py dumpdata inventory`",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        json_file = options.get("json_file")
        if json_file:
            with open(json_file, "r", encoding="utf-8") as jf:
                loaded_data = json.load(jf)
        else:
            loaded_data = data

        if not loaded_data:
            self.stdout.write(self.style.ERROR("Aucune donnée fournie."))
            return

        # Registres internes pour résolution des FK
        objects = {
            "inventory.category": {},
            "inventory.unitofmesure": {},
            "inventory.producttype": {},
            "inventory.locationtype": {},
            "inventory.stocklocation": {},
            "inventory.operationtype": {},
            "inventory.product": {},
            "inventory.productlocation": {},
        }

        # Prioriser l'ordre pour éviter les dépendances manquantes
        priority = {
            "inventory.locationtype": 10,
            "inventory.category": 20,
            "inventory.unitofmesure": 30,
            "inventory.producttype": 40,
            "inventory.operationtype": 50,
            "inventory.stocklocation": 60,
            "inventory.product": 70,
            "inventory.productlocation": 80,
        }
        # Trié par priorité puis par pk pour stabilité
        loaded_data.sort(key=lambda x: (priority.get(x["model"], 99), x["pk"]))

        for item in loaded_data:
            model_name = item["model"]
            pk = item["pk"]
            fields = item["fields"]

            try:
                # ----------------------------- CATEGORY -----------------------------
                if model_name == "inventory.category":
                    obj = Category.objects.create(
                        categ_id=pk,
                        label=fields["label"],
                        description=fields.get("description")
                    )
                    objects[model_name][pk] = obj

                # ------------------------- UNIT OF MESURE --------------------------
                elif model_name == "inventory.unitofmesure":
                    obj = UnitOfMesure.objects.create(
                        uom_id=pk,
                        label=fields["label"],
                        symbole=fields["symbole"]
                    )
                    objects[model_name][pk] = obj

                # --------------------------- PRODUCT TYPE --------------------------
                elif model_name == "inventory.producttype":
                    obj = ProductType.objects.create(
                        product_type_id=pk,
                        label=fields["label"]
                    )
                    objects[model_name][pk] = obj

                # --------------------------- LOCATION TYPE -------------------------
                elif model_name == "inventory.locationtype":
                    obj = LocationType.objects.create(
                        location_type_id=pk,
                        label=fields["label"],
                        description=fields.get("description")
                    )
                    objects[model_name][pk] = obj

                # ----------------------------- STOCK LOCATION ----------------------
                elif model_name == "inventory.stocklocation":
                    obj = StockLocation.objects.create(
                        location_id=pk,
                        name=fields["name"],
                        parent_location=objects["inventory.stocklocation"].get(fields["parent_location"]) if fields["parent_location"] else None,
                        location_type=objects["inventory.locationtype"][fields["location_type"]]
                    )
                    objects[model_name][pk] = obj

                # ---------------------------- OPERATION TYPE -----------------------
                elif model_name == "inventory.operationtype":
                    obj = OperationType.objects.create(
                        operation_type_id=pk,
                        label=fields["label"]
                    )
                    objects[model_name][pk] = obj

                # ------------------------------- PRODUCT ---------------------------
                elif model_name == "inventory.product":
                    obj = Product.objects.create(
                        product_id=pk,
                        name=fields["name"],
                        default_code=fields.get("default_code"),
                        barcode=fields.get("barcode"),
                        standard_price=Decimal(fields["standard_price"]),
                        description=fields.get("description"),
                        active=fields["active"],
                        image_1920=fields.get("image_1920"),
                        weight=fields.get("weight") or 0,
                        volume=fields.get("volume") or 0,
                        dlc=parse_date(fields["dlc"]) if fields.get("dlc") else None,
                        stock_minimal=fields.get("stock_minimal") or 0,
                        categ=objects["inventory.category"].get(fields["categ"]) if fields.get("categ") else None,
                        uom=objects["inventory.unitofmesure"].get(fields["uom"]) if fields.get("uom") else None,
                        product_type=objects["inventory.producttype"].get(fields["product_type"]) if fields.get("product_type") else None,
                        total_quantity_cached=Decimal(fields["total_quantity_cached"]),
                    )
                    objects[model_name][pk] = obj

                # --------------------------- PRODUCT / LOCATION --------------------
                elif model_name == "inventory.productlocation":
                    obj = ProductLocation.objects.create(
                        product_location_id=pk,
                        product=objects["inventory.product"][fields["product"]],
                        location=objects["inventory.stocklocation"][fields["location"]],
                        quantity_stored=Decimal(fields["quantity_stored"]),
                        last_count_date=parse_date(fields["last_count_date"]),
                        quantity_counted=Decimal(fields["quantity_counted"]),
                    )
                    objects[model_name][pk] = obj

                else:
                    # Modèle non géré pour l'instant
                    continue

                self.stdout.write(self.style.SUCCESS(f"Créé {model_name} pk={pk}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur pour {model_name} pk={pk}: {e}"))
                raise

        self.stdout.write(self.style.SUCCESS("Données inventory insérées avec succès."))
