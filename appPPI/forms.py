# forms.py
from django import forms
from loginapp.models import Ejercicio

class MuscleForm(forms.Form):
    muscle = forms.CharField(label='Musculo', max_length=100)

class EjercicioForm(forms.ModelForm):
    class Meta:
        model = Ejercicio
        fields = ['nombre', 'repeticiones', 'peso']

