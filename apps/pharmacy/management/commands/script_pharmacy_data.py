from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import datetime
import json

# --- Purchases dependencies (city, country, language) ---
from apps.purchases.models.country import Country
from apps.purchases.models.city import City
from apps.purchases.models.language import Language

# --- Pharmacy models ---
from apps.pharmacy.models.pharmaceutical_form import PharmaceuticalForm
from apps.pharmacy.models.supplier import PharmacySupplier
from apps.pharmacy.models.dci import Dci
from apps.pharmacy.models.pharmacy import Pharmacy
from apps.pharmacy.models.location_type import PharmacyLocationType
from apps.pharmacy.models.stock_location import PharmacyStockLocation
from apps.pharmacy.models.pharmacy_product_uom import PharmacyUnitOfMesure
from apps.pharmacy.models.pharmacy_product_category import PharmacyProductCategory
from apps.pharmacy.models.product import PharmacyProduct
from apps.pharmacy.models.product_location import PharmacyProductLocation
from apps.pharmacy.models.pharmacy_operation_type import PharmacyOperationType


data = [
    {"model": "pharmacy.pharmaceuticalform", "pk": 1, "fields": {"name": "Forme Gal 1", "description": "forme gal 1"}}, 
    {"model": "pharmacy.pharmacyunitofmesure", "pk": 1, "fields": {"label": "metre", "symbole": "m"}}, 
    {"model": "pharmacy.dci", "pk": 1, "fields": {"label": "DCI 1", "description": "DC1"}}, 
    {"model": "pharmacy.pharmacyproductcategory", "pk": 1, "fields": {"label": "Antalgiques", "description": "Médicaments contre la douleur"}}, 
    {"model": "pharmacy.pharmacyproductcategory", "pk": 2, "fields": {"label": "Antibiotiques", "description": "Traitement des infections bactériennes"}}, 
    {"model": "pharmacy.pharmacyproductcategory", "pk": 3, "fields": {"label": "Psychotropes", "description": "Médicaments pour troubles psychiques"}}, 
    {"model": "pharmacy.pharmacyproductcategory", "pk": 4, "fields": {"label": "Vitamines", "description": "Compléments vitaminiques"}}, 
    {"model": "pharmacy.pharmacyproductcategory", "pk": 5, "fields": {"label": "Soins externes", "description": "Désinfectants, crèmes, etc."}}, 
    {"model": "pharmacy.pharmacy", "pk": 1, "fields": {"label": "pharmcie 1", "adress": "pahrmacie hay riad"}}, 
    {"model": "pharmacy.pharmacylocationtype", "pk": 1, "fields": {"name": "Type emplacement 1", "description": "Description type emplacement 1"}}, 
    {"model": "pharmacy.pharmacystocklocation", "pk": 1, "fields": {"name": "Poste de stockage 1", "parent_location": None, "location_type": 1, "pharmacy": 1}}, 
    {"model": "pharmacy.pharmacysupplier", "pk": 8, "fields": {"name": "Fournisseur 1", "is_company": True, "street": "mabrouka", "street2": "mabrouka", "zip": "", "city": 1, "country": 1, "lang": 1, "email": "yassine@gmail.com", "phone": "0773694763", "mobile": "0773694763", "ICE": "12345678", "RC": 12345678, "IF": 12345678, "vat": "1232425", "RIB": "122342", "comment": "fournisseur 1", "logo": "supplier_logos/Fournisseur_1_20250816_174314.png"}}, 
    {"model": "pharmacy.pharmacyproduct", "pk": 7, "fields": {"code": "PHPDT-0001", "short_label": "P1", "brand": "Dolidol", "full_label": "Produit  1", "dci": 1, "pharmaceutical_form": 1, "dosage": "12", "barcode": "123456", "ppm_price": "12.00", "unit_price": "14.00", "supplier_price": "12.00", "internal_purchase_price": "13.00", "refund_price": "12.00", "refund_rate": "80.00", "uom": 1, "categ": 1, "total_quantity_cached": "26.00", "nombrepiece": 12}}, 
    {"model": "pharmacy.pharmacyproductlocation", "pk": 1, "fields": {"product": 7, "location": 1, "quantity_stored": "26.00", "quantity_counted": "0.00", "last_count_date": "2025-08-16"}}, 
    {"model": "pharmacy.pharmacyoperationtype", "pk": 1, "fields": {"label": "Transfert interne"}}
]


def parse_date(date_str: str):
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    return None


class Command(BaseCommand):
    help = "Insère les données dumpdata pour l'app pharmacy (produits, fournisseurs, etc.)"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            nargs="?",
            help="Chemin optionnel vers le fichier JSON exporté via `python manage.py dumpdata pharmacy`",
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

        objects = {
            "pharmacy.pharmaceuticalform": {},
            "pharmacy.pharmacyunitofmesure": {},
            "pharmacy.dci": {},
            "pharmacy.pharmacyproductcategory": {},
            "pharmacy.pharmacy": {},
            "pharmacy.pharmacylocationtype": {},
            "pharmacy.pharmacystocklocation": {},
            "pharmacy.pharmacyproduct": {},
            "pharmacy.pharmacyproductlocation": {},
            "pharmacy.pharmacysupplier": {},
            "pharmacy.pharmacyoperationtype": {},
        }

        priority = {
            "pharmacy.pharmaceuticalform": 10,
            "pharmacy.pharmacyunitofmesure": 15,
            "pharmacy.dci": 20,
            "pharmacy.pharmacyproductcategory": 25,
            "pharmacy.pharmacy": 30,
            "pharmacy.pharmacylocationtype": 35,
            "pharmacy.pharmacystocklocation": 40,
            "pharmacy.pharmacysupplier": 45,
            "pharmacy.pharmacyproduct": 50,
            "pharmacy.pharmacyproductlocation": 60,
            "pharmacy.pharmacyoperationtype": 70,
        }
        loaded_data.sort(key=lambda x: (priority.get(x["model"], 99), x["pk"]))

        for item in loaded_data:
            model_name = item["model"]
            pk = item["pk"]
            fields = item["fields"]

            try:
                # ------------------ Pharmaceutical Form ------------------
                if model_name == "pharmacy.pharmaceuticalform":
                    obj = PharmaceuticalForm.objects.create(
                        id=pk,
                        name=fields["name"],
                        description=fields.get("description", ""),
                    )
                    objects[model_name][pk] = obj

                # ------------------ Pharmacy Unit of Mesure -------------
                elif model_name == "pharmacy.pharmacyunitofmesure":
                    obj = PharmacyUnitOfMesure.objects.create(
                        uom_id=pk,
                        label=fields["label"],
                        symbole=fields["symbole"],
                    )
                    objects[model_name][pk] = obj

                # ------------------ DCI ---------------------------------
                elif model_name == "pharmacy.dci":
                    obj = Dci.objects.create(
                        dci_id=pk,
                        label=fields["label"],
                        description=fields.get("description", ""),
                    )
                    objects[model_name][pk] = obj

                # ------------------ Category ----------------------------
                elif model_name == "pharmacy.pharmacyproductcategory":
                    obj = PharmacyProductCategory.objects.create(
                        categ_id=pk,
                        label=fields["label"],
                        description=fields.get("description", ""),
                    )
                    objects[model_name][pk] = obj

                # ------------------ Pharmacy ----------------------------
                elif model_name == "pharmacy.pharmacy":
                    obj = Pharmacy.objects.create(
                        pharmacy_id=pk,
                        label=fields["label"],
                        adress=fields.get("adress", ""),
                    )
                    objects[model_name][pk] = obj

                # ------------------ Location Type -----------------------
                elif model_name == "pharmacy.pharmacylocationtype":
                    obj = PharmacyLocationType.objects.create(
                        location_type_id=pk,
                        name=fields["name"],
                        description=fields.get("description", ""),
                    )
                    objects[model_name][pk] = obj

                # ------------------ Stock Location ----------------------
                elif model_name == "pharmacy.pharmacystocklocation":
                    obj = PharmacyStockLocation.objects.create(
                        location_id=pk,
                        name=fields["name"],
                        parent_location=objects["pharmacy.pharmacystocklocation"].get(fields.get("parent_location")) if fields.get("parent_location") else None,
                        location_type=objects["pharmacy.pharmacylocationtype"][fields["location_type"]],
                        pharmacy=objects["pharmacy.pharmacy"].get(fields.get("pharmacy")) if fields.get("pharmacy") else None,
                    )
                    objects[model_name][pk] = obj

                # ------------------ Supplier ----------------------------
                elif model_name == "pharmacy.pharmacysupplier":
                    obj = PharmacySupplier.objects.create(
                        id=pk,
                        name=fields["name"].strip(),
                        is_company=fields["is_company"],
                        street=fields.get("street", ""),
                        street2=fields.get("street2", ""),
                        zip=fields.get("zip", ""),
                        city=City.objects.filter(id=fields.get("city")).first() if fields.get("city") else None,
                        country=Country.objects.filter(id=fields.get("country")).first() if fields.get("country") else None,
                        lang=Language.objects.filter(id=fields.get("lang")).first() if fields.get("lang") else None,
                        email=fields.get("email", ""),
                        phone=fields.get("phone", ""),
                        mobile=fields.get("mobile", ""),
                        ICE=fields.get("ICE", ""),
                        RC=fields.get("RC"),
                        IF=fields.get("IF"),
                        vat=fields.get("vat", ""),
                        RIB=fields.get("RIB", ""),
                        comment=fields.get("comment", ""),
                        logo=fields.get("logo"),
                    )
                    objects[model_name][pk] = obj

                # ------------------ Product -----------------------------
                elif model_name == "pharmacy.pharmacyproduct":
                    obj = PharmacyProduct.objects.create(
                        product_id=pk,
                        code=fields["code"],
                        short_label=fields["short_label"],
                        brand=fields.get("brand"),
                        full_label=fields.get("full_label"),
                        dci=objects["pharmacy.dci"].get(fields.get("dci")) if fields.get("dci") else None,
                        pharmaceutical_form=objects["pharmacy.pharmaceuticalform"].get(fields.get("pharmaceutical_form")) if fields.get("pharmaceutical_form") else None,
                        dosage=fields.get("dosage"),
                        barcode=fields.get("barcode"),
                        ppm_price=Decimal(fields.get("ppm_price", "0")),
                        unit_price=Decimal(fields.get("unit_price", "0")),
                        supplier_price=Decimal(fields.get("supplier_price", "0")),
                        internal_purchase_price=Decimal(fields.get("internal_purchase_price", "0")),
                        refund_price=Decimal(fields.get("refund_price", "0")),
                        refund_rate=Decimal(fields.get("refund_rate", "0")),
                        uom=objects["pharmacy.pharmacyunitofmesure"].get(fields.get("uom")) if fields.get("uom") else None,
                        categ=objects["pharmacy.pharmacyproductcategory"].get(fields.get("categ")) if fields.get("categ") else None,
                        total_quantity_cached=Decimal(fields.get("total_quantity_cached", "0")),
                        nombrepiece=fields.get("nombrepiece"),
                    )
                    objects[model_name][pk] = obj

                # ------------------ Product Location --------------------
                elif model_name == "pharmacy.pharmacyproductlocation":
                    obj = PharmacyProductLocation.objects.create(
                        id=pk,
                        product=objects["pharmacy.pharmacyproduct"][fields["product"]],
                        location=objects["pharmacy.pharmacystocklocation"][fields["location"]],
                        quantity_stored=Decimal(fields["quantity_stored"]),
                        quantity_counted=Decimal(fields["quantity_counted"]),
                        last_count_date=parse_date(fields.get("last_count_date")),
                    )
                    objects[model_name][pk] = obj

                # ------------------ Operation Type ----------------------
                elif model_name == "pharmacy.pharmacyoperationtype":
                    obj = PharmacyOperationType.objects.create(
                        operation_type_id=pk,
                        label=fields["label"],
                    )
                    objects[model_name][pk] = obj

                else:
                    continue

                self.stdout.write(self.style.SUCCESS(f"Créé {model_name} pk={pk}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur pour {model_name} pk={pk}: {e}"))
                raise

        self.stdout.write(self.style.SUCCESS("Données pharmacy insérées avec succès."))
