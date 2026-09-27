from django import forms

from shopapp.models import Product


class MultipleFileInput(forms.FileInput):
    """Виджет, поддерживающий загрузку нескольких файлов."""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Поле формы для загрузки нескольких файлов."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"multiple": True, "class": "form-control"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "price", "description", "discount", "preview")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название продукта"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Описание"}),
            "discount": forms.NumberInput(attrs={"class": "form-control", "min": "0", "max": "100"}),
            "preview": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    images = MultipleFileField(required=False)


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()