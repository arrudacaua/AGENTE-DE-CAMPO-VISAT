from django.contrib import admin
from .constants import ITENS_PADRAO
from .models import Demanda, ItemChecklist, Evidencia


class ItemChecklistInline(admin.TabularInline):
    model = ItemChecklist
    extra = 0
    readonly_fields = ('item', 'resposta')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 0
    readonly_fields = ('tipo', 'descricao', 'criada_em')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Demanda)
class DemandaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'numero_os', 'processo_sei', 'status', 'prioridade', 'fiscal', 'prazo')
    list_filter = ('status', 'prioridade', 'distrito')
    search_fields = ('numero_os', 'processo_sei', 'descricao', 'bairro', 'endereco')
    inlines = [ItemChecklistInline, EvidenciaInline]
    readonly_fields = ('status', 'assinatura_confirmada', 'homologada', 'relatorio', 'relatorio_vinculado_sei')

    def get_readonly_fields(self, request, obj=None):
        if obj and (obj.status == 'concluida' or obj.homologada):
            return tuple(f.name for f in self.model._meta.fields)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change and Demanda.objects.filter(pk=obj.pk).filter(status='concluida').exists():
            return
        super().save_model(request, obj, form, change)
        if not change:
            ItemChecklist.objects.bulk_create([ItemChecklist(demanda=obj, item=i) for i in ITENS_PADRAO])


class RegistroConsultaAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ItemChecklist, RegistroConsultaAdmin)
admin.site.register(Evidencia, RegistroConsultaAdmin)
