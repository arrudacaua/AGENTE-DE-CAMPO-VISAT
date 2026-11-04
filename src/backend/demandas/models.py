from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Demanda(models.Model):
    STATUS_CHOICES = [
        ("aberta", "Em aberto"),
        ("andamento", "Em andamento"),
        ("concluida", "Concluída"),
    ]
    PRIORIDADE_CHOICES = [
        ("baixa", "Baixa"),
        ("media", "Média"),
        ("alta", "Alta"),
    ]

    numero = models.AutoField(primary_key=True)
    numero_os = models.CharField("Número da OS", max_length=60, blank=True)
    latitude = models.DecimalField("Latitude", max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.DecimalField("Longitude", max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    revisao = models.PositiveIntegerField(default=0, editable=False)
    processo_sei = models.CharField("Processo SEI", max_length=60)
    descricao = models.TextField("Descrição")
    endereco = models.CharField("Endereço", max_length=200)
    distrito = models.CharField("Distrito sanitário", max_length=100)
    bairro = models.CharField("Bairro", max_length=100)
    data_recebimento = models.DateField("Data de recebimento", auto_now_add=True)
    prazo = models.DateField("Prazo")
    fiscal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Fiscal responsável",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="demandas_atribuidas",
    )
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="aberta")
    prioridade = models.CharField("Prioridade", max_length=10, choices=PRIORIDADE_CHOICES, default="media")
    anotacoes = models.TextField("Anotações", blank=True)
    assinatura_confirmada = models.BooleanField("Assinatura confirmada", default=False)
    homologada = models.BooleanField("Homologada pela Gerência", default=False)
    relatorio = models.TextField("Relatório técnico", blank=True)
    relatorio_vinculado_sei = models.BooleanField("Vínculo conceitual com SEI", default=False)

    class Meta:
        ordering = ["prazo", "numero"]
        verbose_name = "Demanda"
        verbose_name_plural = "Demandas"

    def clean(self):
        super().clean()
        if (self.latitude is None) != (self.longitude is None):
            raise ValidationError("Informe latitude e longitude juntas, ou deixe ambas vazias.")

    @property
    def tem_coordenadas(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def fiscal_nome(self):
        return (self.fiscal.get_full_name() or self.fiscal.username) if self.fiscal_id else "Não atribuído"

    def __str__(self):
        return f"Demanda #{self.numero} - SEI {self.processo_sei}"


class ItemChecklist(models.Model):
    RESPOSTAS = [
        ("conforme", "Conforme"),
        ("nao_conforme", "Não conforme"),
    ]
    demanda = models.ForeignKey(Demanda, on_delete=models.CASCADE, related_name="itens_checklist")
    item = models.CharField("Item de verificação", max_length=150)
    resposta = models.CharField("Resposta", max_length=20, choices=RESPOSTAS, blank=True)

    class Meta:
        verbose_name = "Item do checklist"
        verbose_name_plural = "Itens do checklist"

    def __str__(self):
        return f"{self.demanda} - {self.item}"


class Evidencia(models.Model):
    TIPOS = [
        ("foto", "Foto"),
        ("video", "Vídeo"),
        ("audio", "Áudio"),
        ("anotacao", "Anotação"),
    ]
    demanda = models.ForeignKey(Demanda, on_delete=models.CASCADE, related_name="evidencias")
    tipo = models.CharField("Tipo", max_length=20, choices=TIPOS)
    descricao = models.TextField("Descrição ou nome do arquivo")
    criada_em = models.DateTimeField("Data do registro", auto_now_add=True)

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "Evidência"
        verbose_name_plural = "Evidências"

    def __str__(self):
        return f"{self.get_tipo_display()} - Demanda #{self.demanda.numero}"
