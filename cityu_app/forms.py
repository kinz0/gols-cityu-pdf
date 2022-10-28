from django import forms

class PngForm(forms.Form):
    pngfile = forms.FileField(widget=forms.ClearableFileInput(attrs={"multiple": True}))

class ExcelForm(forms.Form):
    excelfile = forms.FileField()