from django.db import migrations


def completar(apps, schema_editor):
    Demanda = apps.get_model('demandas', 'Demanda')
    Item = apps.get_model('demandas', 'ItemChecklist')
    nomes = ['Uso de EPI', 'Validade dos extintores', 'Sinalização de segurança',
             'Rotas de fuga', 'Higiene do ambiente', 'Documentação trabalhista']
    for demanda in Demanda.objects.using(schema_editor.connection.alias).exclude(status='concluida').filter(homologada=False).iterator():
        existentes = set(Item.objects.using(schema_editor.connection.alias).filter(demanda=demanda).values_list('item', flat=True))
        Item.objects.using(schema_editor.connection.alias).bulk_create([
            Item(demanda=demanda, item=nome) for nome in nomes if nome not in existentes])


class Migration(migrations.Migration):
    dependencies = [('demandas', '0002_demanda_latitude_demanda_longitude_demanda_numero_os_and_more')]
    operations = [migrations.RunPython(completar, migrations.RunPython.noop)]
