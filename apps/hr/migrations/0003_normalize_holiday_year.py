from django.db import migrations


def set_year_to_2000(apps, schema_editor):
    Holiday = apps.get_model('hr', 'Holiday')
    seen = set()
    for h in Holiday.objects.order_by('id'):
        if not h.date:
            continue
        key = (h.date.month, h.date.day, h.name)
        if key in seen:
            # remove duplicates keeping the first one
            h.delete()
            continue
        seen.add(key)
        if h.date.year != 2000:
            h.date = h.date.replace(year=2000)
            h.save(update_fields=['date'])


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0002_holiday'),
    ]

    operations = [
        migrations.RunPython(set_year_to_2000, migrations.RunPython.noop),
    ]


