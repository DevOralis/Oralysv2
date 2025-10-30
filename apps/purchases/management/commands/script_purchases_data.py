from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
import json

from apps.purchases.models.country import Country
from apps.purchases.models.city import City
from apps.purchases.models.language import Language
from apps.purchases.models.supplier import Supplier
from apps.purchases.models.taxes import Tax
from apps.purchases.models.currency import Currency
from apps.purchases.models.payment_mode import PaymentMode
from apps.purchases.models.convention_type import ConventionType


data = [
   {"model": "purchases.country", "pk": 1, "fields": {"name": "maroc"}}, {"model": "purchases.city", "pk": 1, "fields": {"name": "marrakech", "country": 1}},
    {"model": "purchases.city", "pk": 3, "fields": {"name": "casablanca", "country": 1}}, {"model": 
"purchases.language", "pk": 1, "fields": {"name": "arabe"}}, {"model": "purchases.supplier", "pk": 4, "fields": {"name": "Ikea", "is_company": True, "street": "Ikea", "street2": "Rue Med V", "zip": "43500", "city": 1, "country": 1, "email": "ikea@gmail.contact", "phone": "0554589687", "mobile": "0987654323", "ICE": "re4327626", "RC": 90, "IF": 9, "lang": 1, "vat": "12", "RIB": "12345789098765432123", "comment": "ikea founitures", "logo": "supplier_logos/Ikea_20250817_165625.png"}}, {"model": "purchases.supplier", "pk": 5, "fields": {"name": "Marjane", "is_company": True, "street": "Marjane", "street2": " Essaada BD les arbres", "zip": "43500", "city": 1, "country": 1, "email": "marjane@contact.com", "phone": "0578998832", "mobile": "0632983893", 
"ICE": "pa24484", "RC": 89, "IF": 90, "lang": 1, "vat": "20", "RIB": "1234578998765432", "comment": "Marjane hypermarche", "logo": "supplier_logos/Marjane_20250817_165759.png"}}, {"model": "purchases.supplier", "pk": 6, "fields": {"name": "Koutoubia", 
"is_company": True, "street": "Koutoubia", "street2": "quartier industriel", "zip": "43500", "city": 1, "country": 1, "email": "koutoubia@contact.com", "phone": "053738922", "mobile": "068297379", "ICE": "re76893", "RC": 34, "IF": 25, "lang": 1, "vat": "20", "RIB": "23456789876543456", "comment": "koutoubia charcuetrie", "logo": "supplier_logos/Koutoubia_20250817_170040.png"}}, {"model": "purchases.tax", "pk": 3, "fields": {"libelle": "tva", "valeur": "20.00"}}, {"model": "purchases.currency", "pk": 1, "fields": {"libelle": "dirham", "abreviation": "DH"}}, {"model": "purchases.paymentmode", "pk": 1, "fields": {"name": "carte", "description": "carte bancaire"}}, {"model": "purchases.conventiontype", "pk": 4, "fields": {"libelle": "contract-cadre"}}
]


class Command(BaseCommand):
    help = "Insère les données dumpdata pour l'app purchases (pays, fournisseurs, etc.)"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            nargs="?",
            help="Chemin optionnel vers le fichier JSON exporté via `python manage.py dumpdata purchases`",
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

        # Registres internes
        objects = {
            "purchases.country": {},
            "purchases.city": {},
            "purchases.language": {},
            "purchases.currency": {},
            "purchases.supplier": {},
            "purchases.tax": {},
            "purchases.paymentmode": {},
            "purchases.conventiontype": {},
        }

        # Priorité d'insertion pour respecter les FK
        priority = {
            "purchases.country": 10,
            "purchases.language": 20,
            "purchases.currency": 25,
            "purchases.city": 30,
            "purchases.supplier": 40,
            "purchases.tax": 50,
            "purchases.paymentmode": 60,
            "purchases.conventiontype": 70,
        }
        loaded_data.sort(key=lambda x: (priority.get(x["model"], 99), x["pk"]))

        for item in loaded_data:
            model_name = item["model"]
            pk = item["pk"]
            fields = item["fields"]

            try:
                # ------------------------------ COUNTRY ----------------------------
                if model_name == "purchases.country":
                    obj = Country.objects.create(id=pk, name=fields["name"])
                    objects[model_name][pk] = obj

                # ------------------------------ CITY -------------------------------
                elif model_name == "purchases.city":
                    obj = City.objects.create(
                        id=pk,
                        name=fields["name"],
                        country=objects["purchases.country"][fields["country"]],
                    )
                    objects[model_name][pk] = obj

                # ----------------------------- LANGUAGE ---------------------------
                elif model_name == "purchases.language":
                    obj = Language.objects.create(id=pk, name=fields["name"])
                    objects[model_name][pk] = obj

                # ------------------------------ SUPPLIER --------------------------
                elif model_name == "purchases.supplier":
                    obj = Supplier.objects.create(
                        id=pk,
                        name=fields["name"].strip(),
                        is_company=fields["is_company"],
                        street=fields.get("street", ""),
                        street2=fields.get("street2", ""),
                        zip=fields.get("zip", ""),
                        city=objects["purchases.city"].get(fields.get("city")) if fields.get("city") else None,
                        country=objects["purchases.country"].get(fields.get("country")) if fields.get("country") else None,
                        email=fields.get("email", ""),
                        phone=fields.get("phone", ""),
                        mobile=fields.get("mobile", ""),
                        ICE=fields.get("ICE", ""),
                        RC=fields.get("RC"),
                        IF=fields.get("IF"),
                        lang=objects["purchases.language"].get(fields.get("lang")) if fields.get("lang") else None,
                        vat=fields.get("vat", ""),
                        RIB=fields.get("RIB", ""),
                        comment=fields.get("comment", ""),
                        logo=fields.get("logo"),
                    )
                    objects[model_name][pk] = obj

                # ------------------------------- TAX ------------------------------
                elif model_name == "purchases.tax":
                    obj = Tax.objects.create(
                        id=pk,
                        libelle=fields["libelle"],
                        valeur=Decimal(fields["valeur"]),
                    )
                    objects[model_name][pk] = obj

                # ------------------------------ CURRENCY --------------------------
                elif model_name == "purchases.currency":
                    obj = Currency.objects.create(
                        id=pk,
                        libelle=fields["libelle"],
                        abreviation=fields["abreviation"],
                    )
                    objects[model_name][pk] = obj

                # --------------------------- PAYMENT MODE -------------------------
                elif model_name == "purchases.paymentmode":
                    obj = PaymentMode.objects.create(
                        id=pk,
                        name=fields["name"],
                        description=fields.get("description", ""),
                    )
                    objects[model_name][pk] = obj

                # ------------------------- CONVENTION TYPE ------------------------
                elif model_name == "purchases.conventiontype":
                    obj = ConventionType.objects.create(
                        id=pk,
                        libelle=fields["libelle"],
                    )
                    objects[model_name][pk] = obj

                else:
                    continue

                self.stdout.write(self.style.SUCCESS(f"Créé {model_name} pk={pk}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur pour {model_name} pk={pk}: {e}"))
                raise

        self.stdout.write(self.style.SUCCESS("Données purchases insérées avec succès."))
