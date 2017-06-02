from django import forms
from django.db import models
from django.forms import ModelForm
from django.db import connection
from functools import partial
import cx_Oracle

DateInput = partial(forms.DateInput, {'class':'datepicker'})
class ChoiceFieldNoValidation(forms.ChoiceField):
    def validate(self, value):
        pass

class update_address(forms.Form):
    def __init__(self, *args, **kwargs):
        super(update_address, self).__init__(*args, **kwargs)
    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_country', [rawCursor])
    res = rawCursor.fetchall()

    Nombre = forms.CharField(max_length=100, required = True, widget=forms.TextInput(attrs={'placeholder': 'Nombre', 'class':'form-control'}))

    Apellido = forms.CharField(max_length=100, required = True, widget=forms.TextInput(attrs={'placeholder': 'Apellido', 'class':'form-control'}))

    Correo = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Correo', 'class':'form-control'}))

    Paises = forms.ChoiceField(choices=res, required = True, widget=forms.Select(attrs={ 'class':'form-control'}))

    Estados = ChoiceFieldNoValidation(required=True, widget=forms.Select(attrs={'placeholder': 'Estado','class':'form-control'}))

    Ciudades = ChoiceFieldNoValidation(required=True, widget=forms.Select(attrs={'placeholder': 'Estado','class':'form-control'}))

    Direccion = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Dirección', 'class':'form-control'}))

    Numero_Exterior = forms.IntegerField(required=True, max_value=10000, widget=forms.TextInput(attrs={'placeholder': 'Numero Exterior', 'class':'form-control'}))

    Sexo = forms.ChoiceField(choices={(0,'Seleccione su género'),('M','Masculino'),('F', 'Femenino')}, required=True, widget=forms.Select(attrs={'placeholder': 'Sexo','class':'form-control'}))

    Celular = forms.IntegerField(max_value=10000000000, required=True, widget=forms.TextInput(attrs={'placeholder': 'Celular', 'class':'form-control'}))

    cur.callproc('dientes.get_pkg.get_blood',[rawCursor])
    res=rawCursor.fetchall()

    Tipo_Sangre = forms.ChoiceField(choices=res, required=True, widget=forms.Select(attrs={'placeholder': 'Tipo de Sangre','class':'form-control'}))


class user_groups(forms.Form):
    def __init__(self, *args, **kwargs):
        super(user_groups, self).__init__(*args, **kwargs)
    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_usernames', [rawCursor])

    res = rawCursor.fetchall()

    Usuarios = forms.ChoiceField(choices=res, required=True)

    cur.callproc('dientes.get_pkg.get_groups', [rawCursor])

    res = rawCursor.fetchall()

    Grupos = forms.ChoiceField(choices=res,required=True)

class forma_cita_id(forms.Form):
    Cita_Id = forms.IntegerField()

class nueva_cita_doc(forms.Form):
    def __init__(self, *args, **kwargs):
        super(nueva_cita_doc, self).__init__(*args, **kwargs)
    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_paciente_cita', [rawCursor])
    res = rawCursor.fetchall()


    Pacientes = forms.ChoiceField(choices=res, required=True, widget=forms.Select(attrs={'placeholder': 'Paciente', 'class':'form-control'}))
    Detalle = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Detalle', 'class':'form-control'}), required = True)
    Fecha = forms.DateField(widget=DateInput(format='%m/%d/%Y'), required=True)
    Hora = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}, format='%H:%M'), required=True)

class nueva_cita_paciente(forms.Form):
    def __init__(self, *args, **kwargs):
        super(nueva_cita_paciente, self).__init__(*args, **kwargs)
    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_doctor', [rawCursor])

    res = rawCursor.fetchall()
    res2 = []
    i=0
    for item in res:
        nombre = item[1] + ' ' + item[2]
        res2.append((item[0], nombre))

    Doctores = forms.ChoiceField(choices=res2, required=True, widget=forms.Select(attrs={'class':'form-control'}))
    Detalle = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Detalle', 'class':'form-control'}), required = True)
    Fecha = forms.DateField(widget= DateInput(), required=True)
    Hora = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}, format='%H:%M'), required=True)

class nueva_cita_admin(forms.Form):
    def __init__(self, *args, **kwargs):
        super(nueva_cita_admin, self).__init__(*args, **kwargs)
    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_doctor', [rawCursor])

    res = rawCursor.fetchall()
    res2 = []
    i = 0
    for item in res:
        nombre = item[1] + ' ' + item[2]
        res2.append((item[0], nombre))

    Doctores = forms.ChoiceField(choices=res2, required=True)

    cur.callproc('dientes.get_pkg.get_paciente_cita', [rawCursor])
    res = rawCursor.fetchall()

    Pacientes = forms.ChoiceField(choices=res, required=True)
    Detalle = forms.CharField(widget=forms.Textarea, required=True)
    Fecha = forms.DateField(widget=DateInput(), required=True)
    Hora = forms.TimeField(widget=forms.TimeInput( attrs={'class': 'timepicker'}, format='%H:%M'), required=True)

class forma_horarios_Inicio(forms.Form):
    Lunes_Inicio = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Martes_Inicio = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Miercoles_Inicio = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Jueves_Inicio = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Viernes_Inicio = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Sabado_Inicio = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Domingo_Inicio = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)

class forma_horarios_Fin(forms.Form):
    Lunes_Fin = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Martes_Fin = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Miercoles_Fin = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Jueves_Fin = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Viernes_Fin = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Sabado_Fin = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)
    Domingo_Fin = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'timepicker'}), input_formats=['%I:%M%p', '%I:%M %p'], required=False)

class forma_tratamientos(forms.Form):
    def __init__(self, *args, **kwargs):
        super(forma_tratamientos, self).__init__(*args, **kwargs)
    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_especialidades', [rawCursor])
    res = rawCursor.fetchall()

    Nombre = forms.CharField(max_length=100, required = True)

    Especialidad = forms.ChoiceField(choices=res, required = True)

    Costo = forms.CharField(required=True)

class doc_tratamientos_pacientes(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(doc_tratamientos_pacientes, self).__init__(*args, **kwargs)

    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_paciente_cita', [rawCursor])
    res = rawCursor.fetchall()

    Pacientes = forms.ChoiceField(choices=res, required=True)

    cur.callproc('dientes.get_pkg.get_tratamientos', [rawCursor])

    res = rawCursor.fetchall()
    res2 = []

    for item in res:
        res2.append((item[0],item[1]))
    Tratamientos = forms.ChoiceField(choices=res2, required = True)
    Costo = forms.DecimalField(disabled=True, required=False)
    Citas = forms.IntegerField(required=True)
    dias = [(0,'Seleccione un día'),('Lunes','Lunes'), ('Martes','Martes'), ('Miercoles','Miercoles'), ('Jueves','Jueves'), ('Viernes','Viernes'), ('Sabado','Sabado'), ('Domingo','Domingo')]
    Dia = forms.ChoiceField(choices=dias)
    Hora_Preferencia = forms.TimeField(widget=forms.TimeInput( attrs={'class': 'timepicker'}, format='%H:%M'), required=True)

class admn_tratamientos_pacientes(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(admn_tratamientos_pacientes, self).__init__(*args, **kwargs)

    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_doctor', [rawCursor])

    res = rawCursor.fetchall()
    res2 = []
    i = 0
    for item in res:
        nombre = item[1] + ' ' + item[2]
        res2.append((item[0], nombre))

    Doctores = forms.ChoiceField(choices=res2, required=True)

    cur.callproc('dientes.get_pkg.get_paciente_cita', [rawCursor])
    res = rawCursor.fetchall()

    Pacientes = forms.ChoiceField(choices=res, required=True)

    cur.callproc('dientes.get_pkg.get_tratamientos', [rawCursor])

    res = rawCursor.fetchall()
    res2 = []

    for item in res:
        res2.append((item[0],item[1]))
    Tratamientos = ChoiceFieldNoValidation(choices=res2, required = True)
    Costo = forms.DecimalField(disabled=True, required=False)
    Citas = forms.IntegerField(required=True)
    dias = [(0,'Seleccione un día'),('Lunes','Lunes'), ('Martes','Martes'), ('Miercoles','Miercoles'), ('Jueves','Jueves'), ('Viernes','Viernes'), ('Sabado','Sabado'), ('Domingo','Domingo')]
    Dia = forms.ChoiceField(choices=dias)
    Hora_Preferencia = forms.TimeField(widget=forms.TimeInput( attrs={'class': 'timepicker'}, format='%H:%M'), required=True)

class forma_pagos(forms.Form):
    def __init__(self, *args, **kwargs):
        super(forma_pagos, self).__init__(*args, **kwargs)

    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_doctor', [rawCursor])

    res = rawCursor.fetchall()
    res2 = []
    i = 0
    for item in res:
        nombre = item[1] + ' ' + item[2]
        res2.append((item[0], nombre))

    Doctores = forms.ChoiceField(choices=res2, required=True)
    Pacientes = ChoiceFieldNoValidation(required=True)
    Tratamiento = ChoiceFieldNoValidation(required=True)
    Total = forms.DecimalField(required=True, decimal_places=2)

    cur.callproc('dientes.get_pkg.get_tipo_pago', [rawCursor])
    res = rawCursor.fetchall()

    Tipo_Pago = forms.ChoiceField(choices=res, required=True)

class agregar_material(forms.Form):
    Material = forms.CharField(required=True)

class forma_tipo_cambio(forms.Form):
    Tipo_Cambio = forms.DecimalField(required=True, decimal_places=2)

class agregar_alergia(forms.Form):

    Alergia = forms.CharField(required=True)

class alergia_paciente(forms.Form):
    def __init__(self, *args, **kwargs):
        super(alergia_paciente, self).__init__(*args, **kwargs)

    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_alergia', [rawCursor])
    res = rawCursor.fetchall()

    Alergia = forms.MultipleChoiceField(choices=res, widget=forms.CheckboxSelectMultiple, required = False)

class alergia_paciente_admn(forms.Form):
    def __init__(self, *args, **kwargs):
        super(alergia_paciente_admn, self).__init__(*args, **kwargs)

    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_paciente_cita', [rawCursor])
    res = rawCursor.fetchall()

    Pacientes = forms.ChoiceField(choices=res, required=True)

    cur.callproc('dientes.get_pkg.get_alergia', [rawCursor])
    res = rawCursor.fetchall()

    Alergia = forms.MultipleChoiceField(choices=res,widget=forms.CheckboxSelectMultiple, required = False)

class enfermedad_paciente(forms.Form):
    def __init__(self, *args, **kwargs):
        super(enfermedad_paciente, self).__init__(*args, **kwargs)

    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_enfermedad', [rawCursor])
    res = rawCursor.fetchall()

    Enfermedad = forms.MultipleChoiceField(choices=res, widget=forms.CheckboxSelectMultiple, required = False)

class enfermedad_paciente_admn(forms.Form):
    def __init__(self, *args, **kwargs):
        super(enfermedad_paciente_admn, self).__init__(*args, **kwargs)

    cur = connection.cursor()
    rawCursor = cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_enfermedad', [rawCursor])
    res = rawCursor.fetchall()

    Enfermedad = forms.MultipleChoiceField(choices=res,widget=forms.CheckboxSelectMultiple, required = False)