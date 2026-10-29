"""Prepara apenas o banco descartavel do GitHub Actions para demonstracao."""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from datetime import date, timedelta
from django.contrib.auth.models import User
from demandas.models import Demanda, ItemChecklist
from demandas.constants import ITENS_PADRAO

gerente, _ = User.objects.get_or_create(username="gerencia_demo")
gerente.set_password("DemoGerencia123!")
gerente.is_staff = True
gerente.save()
fiscal, _ = User.objects.get_or_create(username="fiscal_demo")
fiscal.set_password("DemoFiscal123!")
fiscal.is_staff = False
fiscal.save()
demanda, _ = Demanda.objects.get_or_create(
    processo_sei="SEI-DEMO-ENTREGA03",
    defaults=dict(numero_os="OS-DEMO-001", descricao="Inspecao demonstrativa para validacao da Sprint 01",
        endereco="Rua Exemplo, 100", distrito="Distrito IV", bairro="Casa Amarela",
        prazo=date.today() + timedelta(days=10), fiscal=fiscal, status="aberta", prioridade="media"),
)
for item in ITENS_PADRAO:
    ItemChecklist.objects.get_or_create(demanda=demanda, item=item)
print("Dados ficticios criados. Demanda:", demanda.numero)
