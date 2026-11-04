from django import forms
from django.contrib.auth import get_user_model
from .models import Demanda, ItemChecklist, Evidencia

User = get_user_model()


class DemandaForm(forms.ModelForm):
    class Meta:
        model = Demanda
        fields = [
            "numero_os", "processo_sei", "descricao", "endereco", "distrito", "bairro",
            "prazo", "fiscal", "prioridade", "latitude", "longitude",
        ]
        widgets = {
            "prazo": forms.DateInput(attrs={"type": "date"}),
            "descricao": forms.Textarea(attrs={"rows": 4, "placeholder": "Descreva o motivo da demanda e o que precisa ser verificado"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fiscal"].queryset = User.objects.filter(is_active=True, is_staff=False, is_superuser=False).exclude(groups__name="Gerencia").distinct()

        self.fields["numero_os"].help_text = "Identificador da ordem de serviço, se existir. É separado do número automático da demanda."
        self.fields["latitude"].help_text = "Coordenada do local da inspeção, entre -90 e 90. Opcional."
        self.fields["longitude"].help_text = "Entre -180 e 180. Preencha junto com a latitude. Use ponto decimal."


class LocalizacaoForm(forms.ModelForm):
    class Meta:
        model = Demanda
        fields = ["endereco", "bairro", "distrito", "latitude", "longitude"]


class RespostasChecklistForm(forms.Form):
    revisao = forms.IntegerField(min_value=0, widget=forms.HiddenInput)

    def __init__(self, *args, itens, **kwargs):
        super().__init__(*args, **kwargs)
        for item in itens:
            self.fields[f"item_{item.pk}"] = forms.ChoiceField(
                label=item.item, required=False,
                choices=[("", "Pendente"), *ItemChecklist.RESPOSTAS],
                initial=item.resposta, widget=forms.RadioSelect,
            )

    def clean(self):
        data = super().clean()
        if self.is_bound:
            allowed = set(self.fields)
            for key in self.data:
                if key.startswith("item_") and key not in allowed:
                    raise forms.ValidationError("Item não pertence a este checklist. Nenhuma resposta foi alterada.")
                if key in allowed and len(self.data.getlist(key)) != 1:
                    raise forms.ValidationError("Envie apenas uma resposta por item.")
        return data


class ChecklistForm(forms.ModelForm):
    class Meta:
        model = ItemChecklist
        fields = ["resposta"]


class EvidenciaForm(forms.ModelForm):
    class Meta:
        model = Evidencia
        fields = ["tipo", "descricao"]
        widgets = {"descricao": forms.Textarea(attrs={"rows": 4, "placeholder": "Descreva o registro realizado em campo"})}
