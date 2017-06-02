from django.shortcuts import redirect, render
from django.db import connection
from testing import forms
from testing import settings
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import django_tables2 as tables
from django.db import models
from django_tables2 import RequestConfig, A
from django.utils.html import format_html
from registro import  models
from django.contrib import messages

def getTable(cursor, metodo):
    exptData = dictfetchall(cursor)
    class NameTable(tables.Table):
        if metodo == 'tablapacientes':
            ID = tables.Column()
            PACIENTE = tables.Column()
        elif metodo == 'tablacitas':
            ID_CITA = tables.Column()
            PACIENTE = tables.Column()
            DENTISTA = tables.Column()
            FECHA_HORA = tables.Column()
            ACEPTADA = tables.Column()
            DETALLE = tables.Column()
            ASISTIO = tables.Column()
        elif metodo == 'tablatratamientos':
            ID_TRATAMIENTO = tables.Column()
            NOMBRE = tables.Column()
            ESPECIALIDAD = tables.Column()
            COSTO = tables.Column()
        elif metodo == 'tablaabonos':
            ID_ABONOS = tables.Column()
            PACIENTE = tables.Column()
            NOMBRE = tables.Column(verbose_name="TRATAMIENTO")
            FECHA = tables.Column(verbose_name="FECHA LIMITE DE PAGO")
            COSTO = tables.Column()
            PAGADO = tables.Column()
        elif metodo == 'tablamateriales':
            ID_MATERIAL = tables.Column()
            NOMBRE = tables.Column(verbose_name='MATERIAL')
        elif metodo == 'tablapagos':
            ID_PAGO= tables.Column()
            FECHA= tables.Column()
            NOMBRE= tables.Column()
            TOTAL= tables.Column()
            PACIENTE= tables.Column()
            DENTISTA= tables.Column()
        elif metodo == 'tablaalergia':
            ID_ALERGIA = tables.Column()
            NOMBRE = tables.Column(verbose_name='ALERGIA')
        class Meta:
            attrs={"class":"table table-hover table-vcenter table-responsive", "id":"tablamamalona"}

    table = NameTable(exptData)
    return table

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def login_redirect(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    else:
        return redirect('/home')

def update_user_info(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
            basehtml = 'bases/basepaciente.html'
        else:
            grupo = str(groups[0])
        if grupo =="Doctores":
            basehtml = 'bases/basedentista.html'
        elif grupo=="Administrador":
            basehtml = 'bases/baseadministrador.html'
        if request.method == "POST":
            form = forms.update_address(request.POST)
            if form.is_valid():
                cur = connection.cursor()
                rawCursor = cur.connection.cursor()
                nombre = request.POST.get('Nombre')
                apellido = request.POST.get('Apellido')
                correo = request.POST.get('Correo')
                ciudad = request.POST.get('Ciudades')
                calle = request.POST.get('Direccion')
                exterior = request.POST.get('Numero_Exterior')
                sexo = request.POST.get('Sexo')
                celular = request.POST.get('Celular')
                blood = request.POST.get('Tipo_Sangre')
                cur.callproc('dientes.get_pkg.get_address_id', [usuario, rawCursor])
                addressid = rawCursor.fetchall()
                if not addressid:
                    cur.callproc('dientes.add_pkg.add_user_info', [usuario, nombre, apellido, correo, ciudad, calle, exterior, sexo, celular, blood])
                else:
                    addressid = addressid[0]
                    addressid = addressid[0]
                    cur.callproc('dientes.EDIT_pkg.EDIT_user_info', [usuario, nombre, apellido, correo, ciudad, calle, exterior, sexo, celular, blood,
                                  addressid])
                    cur.close()
                    return redirect('/home')
        else:
            form = forms.update_address()
        return render(request, 'update_user.html', {'form':form, 'usuario':request.user.username, 'basehtml':basehtml, 'grupo':grupo})

def grupos_usuarios(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        groups = request.user.groups.all()
        grupo = str(groups[0])
        if grupo != "Administrador":
            return redirect('/home')
        else:
            basehtml = 'bases/baseadministrador.html'
            if request.method == "POST":
                form = forms.user_groups(request.POST)
                if form.is_valid():
                    cur = connection.cursor()
                    rawCursor = cur.connection.cursor()
                    usuario = request.POST.get('Usuarios')
                    grupo = request.POST.get('Grupos')
                    cur.callproc('dientes.get_pkg.get_user_group', [usuario, rawCursor])
                    grupoid = rawCursor.fetchall()
                    if not grupoid:
                        cur.callproc('dientes.add_pkg.add_user_group', [usuario, grupo])
                    else:
                        grupoid = grupoid[0]
                        grupoid = grupoid[0]
                        cur.callproc('dientes.edit_pkg.edit_user_group', [grupoid, grupo])
                return redirect('/home')
            else:
                form = forms.user_groups()
            return render(request, 'user_groups.html', {'form':form, 'basehtml':basehtml})

def new_app(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        cur.callproc('dientes.get_pkg.get_address_id', [usuario, rawCursor])
        res = rawCursor.fetchall()
        if not res:
            return redirect('/update_user_info')
        else:
            if not groups:
                grupo="Pacientes"
            else:
                grupo = str(groups[0])
            if grupo == "Doctores":
                basehtml = 'bases/basedentista.html'
                if request.method == "POST":
                    form = forms.nueva_cita_doc(request.POST)
                    if form.is_valid():
                        cur = connection.cursor()
                        rawCursor = cur.connection.cursor()
                        paciente = request.POST.get('Pacientes')
                        fecha = request.POST.get('Fecha')
                        hora = request.POST.get('Hora')
                        fecha = fecha + " " + hora
                        detalle = request.POST.get('Detalle')
                        doctor = usuario
                        citanum = 0
                        aceptada = 1
                        cur.callproc('dientes.functionality.cita_rep', [fecha, citanum, rawCursor])
                        res = rawCursor.fetchall()
                        res = res[0]
                        if res[0] == 1:
                            cur.callproc('dientes.add_pkg.add_cita',[citanum, paciente, doctor, fecha, detalle, 0, aceptada])
                            cur.close()
                            return redirect('/todas_citas')
                        else:
                            messages.warning(request, 'Fecha y/o hora no disponibles')
                            cur.close()
                else:
                    form = forms.nueva_cita_doc()
            elif grupo == "Pacientes":
                basehtml = 'bases/basepaciente.html'
                if request.method == "POST":
                    form = forms.nueva_cita_paciente(request.POST)
                    if form.is_valid():
                        cur = connection.cursor()
                        rawCursor = cur.connection.cursor()
                        paciente = usuario
                        fecha = request.POST.get('Fecha')
                        hora = request.POST.get('Hora')
                        fecha = fecha + " " + hora
                        detalle = request.POST.get('Detalle')
                        doctor = request.POST.get('Doctores')
                        citanum = 0
                        aceptada = 1
                        cur.callproc('dientes.functionality.cita_rep', [fecha, citanum, rawCursor])
                        res = rawCursor.fetchall()
                        res = res[0]
                        if res[0] == 1:
                            cur.callproc('dientes.add_pkg.add_cita',
                                         [citanum, paciente, doctor, fecha, detalle, 0, aceptada])
                            cur.close()
                            return redirect('/todas_citas')
                        else:
                            messages.warning(request, 'Fecha y/o hora no disponibles')
                            cur.close()
                else:
                    form = forms.nueva_cita_paciente()
            elif grupo == "Administrador":
                basehtml = 'bases/baseadministrador.html'
                if request.method == "POST":
                    form = forms.nueva_cita_admin(request.POST)
                    if form.is_valid():
                        cur = connection.cursor()
                        rawCursor = cur.connection.cursor()
                        paciente = request.POST.get('Pacientes')
                        fecha = request.POST.get('Fecha')
                        hora = request.POST.get('Hora')
                        fecha = fecha + " " + hora
                        detalle = request.POST.get('Detalle')
                        doctor = request.POST.get('Doctores')
                        citanum = 0
                        aceptada = 1
                        cur.callproc('dientes.functionality.cita_rep', [fecha, citanum, rawCursor])
                        res = rawCursor.fetchall()
                        res = res[0]
                        if res[0] == 1:
                            cur.callproc('dientes.add_pkg.add_cita', [citanum, paciente, doctor, fecha, detalle, 0, aceptada])
                            cur.close()
                            return redirect('/todas_citas')
                        else:
                            messages.warning(request, 'Fecha y/o hora no disponibles')
                            cur.close()
                else:
                    form = forms.nueva_cita_admin()
        return render(request, 'nueva_cita.html', {'form':form, 'basehtml':basehtml, 'usuario':usuario, 'grupo':grupo})

def edit_app(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        cur.callproc('dientes.get_pkg.get_address_id', [usuario, rawCursor])
        res = rawCursor.fetchall()
        if not res:
            return redirect('/update_user_info')
        else:
            if not groups:
                grupo="Pacientes"
            else:
                grupo = str(groups[0])
            if grupo == "Doctores":
                basehtml = 'bases/basedentista.html'
                if request.method == "POST":
                    form = forms.nueva_cita_doc(request.POST)
                    form2 = forms.forma_cita_id(request.POST)
                    if form.is_valid():
                        cur = connection.cursor()
                        rawCursor = cur.connection.cursor()
                        paciente = request.POST.get('Pacientes')
                        fecha = request.POST.get('Fecha')
                        hora = request.POST.get('Hora')
                        fecha = fecha + " " + hora
                        detalle = request.POST.get('Detalle')
                        doctor = usuario
                        citanum = request.POST.get('Cita_Id')
                        cur.callproc('dientes.functionality.cita_rep', [fecha, citanum, rawCursor])
                        res = rawCursor.fetchall()
                        res = res[0]
                        if res[0] == 1:
                            cur.callproc('dientes.edit_pkg.edit_cita',
                                         [citanum, paciente, doctor, fecha, detalle, 0, 1, 0])
                            cur.close()
                            return HttpResponse('<script type="text/javascript">window.close()</script>')
                        else:
                            messages.warning(request, 'Fecha y/o hora no disponibles')
                            cur.close()
                else:
                    form = forms.nueva_cita_doc()
                    form2 = forms.forma_cita_id()
            elif grupo == "Pacientes":
                basehtml = 'bases/basepaciente.html'
                if request.method == "POST":
                    form = forms.nueva_cita_paciente(request.POST)
                    form2 = forms.forma_cita_id(request.POST)
                    if form.is_valid():
                        cur = connection.cursor()
                        rawCursor = cur.connection.cursor()
                        paciente = usuario
                        fecha = request.POST.get('Fecha')
                        hora = request.POST.get('Hora')
                        fecha = fecha + " " + hora
                        detalle = request.POST.get('Detalle')
                        doctor = request.POST.get('Doctores')
                        citanum = request.POST.get('Cita_Id')
                        cur.callproc('dientes.functionality.cita_rep', [fecha, citanum, rawCursor])
                        res = rawCursor.fetchall()
                        res = res[0]
                        if res[0] == 1:
                            cur.callproc('dientes.edit_pkg.edit_cita',
                                         [citanum, paciente, doctor, fecha, detalle, 0, 1, 0])
                            cur.close()
                            return HttpResponse('<script type="text/javascript">window.close()</script>')
                        else:
                            messages.warning(request, 'Fecha y/o hora no disponibles')
                            cur.close()
                else:
                    form = forms.nueva_cita_paciente()
                    form2 = forms.forma_cita_id()
            elif grupo == "Administrador":
                basehtml = 'bases/baseadministrador.html'
                if request.method == "POST":
                    form = forms.nueva_cita_admin(request.POST)
                    form2 = forms.forma_cita_id(request.POST)
                    if form.is_valid():
                        cur = connection.cursor()
                        rawCursor = cur.connection.cursor()
                        paciente = request.POST.get('Pacientes')
                        fecha = request.POST.get('Fecha')
                        hora = request.POST.get('Hora')
                        fecha = fecha + " " + hora
                        detalle = request.POST.get('Detalle')
                        doctor = request.POST.get('Doctores')
                        citanum = request.POST.get('Cita_Id')
                        cur.callproc('dientes.functionality.cita_rep', [fecha, citanum, rawCursor])
                        res = rawCursor.fetchall()
                        res = res[0]
                        if res[0] == 1:
                            cur.callproc('dientes.edit_pkg.edit_cita',
                                         [citanum, paciente, doctor, fecha, detalle, 0, 1, 0])
                            cur.close()
                            return HttpResponse('<script type="text/javascript">window.close()</script>')
                        else:
                            messages.warning(request, 'Fecha y/o hora no disponibles')
                            cur.close()
                else:
                    form = forms.nueva_cita_admin()
                    form2 = forms.forma_cita_id()
        return render(request, 'editar_cita.html', {'form':form, 'form2':form2, 'basehtml':basehtml, 'usuario':usuario, 'grupo':grupo})

def todas_citas(request):
    def __init__(self, *args, **kwargs):
        super(todas_citas, self).__init__(*args, **kwargs)
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
        else:
            grupo = str(groups[0])
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        if grupo == "Doctores":
            basehtml = 'bases/basedentista.html'
            proc = 'dientes.get_pkg.get_cita_doctor'
            cur.callproc(proc, [rawCursor, usuario])
        elif grupo == "Pacientes":
            basehtml = 'bases/basepaciente.html'
            proc = 'dientes.get_pkg.get_cita_p'
            cur.callproc(proc, [rawCursor, usuario])
        elif grupo == "Administrador":
            basehtml = 'bases/baseadministrador.html'
            proc = 'dientes.get_pkg.get_cita_a'
            cur.callproc(proc, [rawCursor])

        res = rawCursor.fetchall()
        if not res:
            citas = None
            return render(request, 'todas_citas.html', {'citas':citas,'basehtml':basehtml, 'usuario':usuario, 'grupo':grupo})
        else:
            if grupo =="Administrador":
                cur.callproc(proc, [rawCursor])
            else:
                cur.callproc(proc, [rawCursor, usuario])
            tablaFinal = getTable(rawCursor, "tablacitas")
            RequestConfig(request).configure(tablaFinal)


        return render(request, 'todas_citas.html', {'citas':tablaFinal, 'basehtml':basehtml, 'usuario':usuario, 'grupo':grupo})

def citas_confirmar(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        if not groups:
            grupo = "Pacientes"
        else:
            grupo = str(groups[0])
        if grupo == "Doctores":
            basehtml = 'bases/basedentista.html'
            proc = 'dientes.get_pkg.get_cita_na_doctor'
            cur.callproc(proc, [rawCursor, usuario])
        elif grupo == "Pacientes":
            basehtml = 'bases/basepaciente.html'
            proc = 'dientes.get_pkg.get_cita_na_p'
            cur.callproc(proc, [rawCursor, usuario])
        elif grupo == "Administrador":
            basehtml = 'bases/baseadministrador.html'
            proc = 'dientes.get_pkg.get_cita_a_na'
            cur.callproc(proc, [rawCursor])

        res = rawCursor.fetchall()
        if not res:
            citas = None
            return render(request, 'citas_confirmar.html', {'citas':citas, 'basehtml':basehtml, 'usuario':usuario, 'grupo':grupo})
        else:
            if grupo =="Administrador":
                cur.callproc(proc, [rawCursor])
            else:
                cur.callproc(proc, [rawCursor, usuario])
            tablaFinal = getTable(rawCursor, "tablacitas")
            RequestConfig(request).configure(tablaFinal)

        return render(request, 'citas_confirmar.html', {'citas':tablaFinal, 'basehtml':basehtml, 'usuario':usuario, 'grupo':grupo})

def horario_vista(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        if not groups:
            grupo="Paciente"
        else:
            grupo = str(groups[0])
        if grupo == "Doctores":
            basehtml = 'bases/basedentista.html'
            if request.method == "POST":
                form1 = forms.forma_horarios_Inicio(request.POST)
                form2 = forms.forma_horarios_Fin(request.POST)
                if form1.is_valid() and form2.is_valid():
                    cur = connection.cursor()
                    rawCursor = cur.connection.cursor()
                    cur.callproc('dientes.get_pkg.get_horario_doc', [usuario, rawCursor])
                    res = rawCursor.fetchall()
                    if not res:
                        exists = 0
                    else:
                        exists=1
                    lunes1 = request.POST.get('Lunes_Inicio')
                    martes1 = request.POST.get('Martes_Inicio')
                    miercoles1 = request.POST.get('Miercoles_Inicio')
                    jueves1 = request.POST.get('Jueves_Inicio')
                    viernes1 = request.POST.get('Viernes_Inicio')
                    sabado1 = request.POST.get('Sabado_Inicio')
                    domingo1 = request.POST.get('Domingo_Inicio')
                    lunes2 = request.POST.get('Lunes_Fin')
                    martes2 = request.POST.get('Martes_Fin')
                    miercoles2 = request.POST.get('Miercoles_Fin')
                    jueves2 = request.POST.get('Jueves_Fin')
                    viernes2 = request.POST.get('Viernes_Fin')
                    sabado2 = request.POST.get('Sabado_Fin')
                    domingo2 = request.POST.get('Domingo_Fin')
                    lunes = lunes1 + "-" + lunes2
                    martes = martes1 + "-" + martes2
                    miercoles = miercoles1+"-"+miercoles2
                    jueves = jueves1 + "-" + jueves2
                    viernes = viernes1 + "-" + viernes2
                    sabado = sabado1 + "-" + sabado2
                    domingo = domingo1 + "-" + domingo2
                    horario_id = ''
                    if exists == 0:
                        cur.callproc('dientes.add_pkg.add_horario',
                                     [horario_id, usuario, lunes, martes, miercoles, jueves, viernes, sabado, domingo])
                    else:
                        cur.callproc('dientes.edit_pkg.edit_horarios',
                                     [lunes, martes, miercoles, jueves, viernes, sabado, domingo, 1, usuario])
                    return redirect('/home')
            else:
                form1 = forms.forma_horarios_Inicio()
                form2 = forms.forma_horarios_Fin()
            return render(request, 'horarios.html', {'form1': form1, 'form2': form2, 'usuario': usuario, 'grupo': grupo, 'basehtml': basehtml})
        elif grupo == "Paciente" or grupo == "Administrador":
            return redirect('/home')

def pacientes(request):
    def __init__(self, *args, **kwargs):
        super(pacientes, self).__init__(*args, **kwargs)
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        groups = request.user.groups.all()
        if not groups:
            grupo = "Paciente"
        else:
            grupo = str(groups[0])
        if grupo == "Doctores" or grupo == "Administrador":
            cur = connection.cursor()
            rawCursor = cur.connection.cursor()
            if grupo == "Doctores":
                basehtml = 'bases/basedentista.html'
                doctor = request.user.id
                cur.callproc('dientes.get_pkg.get_pacientes_doctor', [doctor, rawCursor])
                res = rawCursor.fetchall()
                if not res:
                    tablaFinal = None
                    return render(request, 'lista_pacientes.html', {'pacientes': tablaFinal, 'basehtml': basehtml})
                else:
                    cur.callproc('dientes.get_pkg.get_pacientes_doctor', [doctor, rawCursor])
                    tablaFinal = getTable(rawCursor, "tablapacientes")
                    RequestConfig(request).configure(tablaFinal)
                    return render(request, 'lista_pacientes.html', {'pacientes':tablaFinal, 'basehtml':basehtml})
            elif grupo == "Administrador":
                basehtml = 'bases/baseadministrador.html'
                cur.callproc('dientes.get_pkg.get_paciente_cita', [rawCursor])
                res = rawCursor.fetchall()
                if not res:
                    tablaFinal = None
                    return render(request, 'lista_pacientes.html', {'pacientes': tablaFinal, 'basehtml': basehtml})
                else:
                    cur.callproc('dientes.get_pkg.get_paciente_cita', [rawCursor])
                    tablaFinal = getTable(rawCursor, "tablapacientes")
                    RequestConfig(request).configure(tablaFinal)
                    return render(request, 'lista_pacientes.html', {'pacientes': tablaFinal, 'basehtml': basehtml})
        else:
            return redirect('/home')

def tratamientos(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
        else:
            grupo = str(groups[0])
        if grupo == "Pacientes":
            basehtml = 'bases/basepaciente.html'
        elif grupo == "Doctores":
            basehtml = 'bases/basedentista.html'
        elif grupo == "Administrador":
            basehtml = 'bases/baseadministrador.html'
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        cur.callproc('dientes.get_pkg.get_tratamientos', [rawCursor])
        res = rawCursor.fetchall()

        if not res:
            tablaFinal = None
        else:
            cur.callproc('dientes.get_pkg.get_tratamientos', [rawCursor])
            tablaFinal = getTable(rawCursor, "tablatratamientos")
            RequestConfig(request).configure(tablaFinal)

    return render(request, 'lista_tratamientos.html', {'tratamientos':tablaFinal, 'basehtml':basehtml, 'grupo': grupo})

def nuevo_tratamiento(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
        else:
            grupo = str(groups[0])
        if grupo == "Pacientes" or grupo == "Doctores":
            return redirect('/home')
        elif grupo == "Administrador":
            basehtml = 'bases/baseadministrador.html'
            if request.method == "POST":
                form = forms.forma_tratamientos(request.POST)
                if form.is_valid():
                    cur = connection.cursor()
                    nombre = request.POST.get("Nombre")
                    costo = request.POST.get("Costo")
                    especialidad = request.POST.get("Especialidad")
                    cur.callproc('dientes.add_pkg.add_tratamiento', [nombre, costo, especialidad])
                    cur.close()
                    return redirect('/home')
            else:
                form = forms.forma_tratamientos()
            return render(request,'nuevo_tratamiento.html', {'form':form, 'basehtml':basehtml})

def asignar_tratamientos(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
        else:
            grupo = str(groups[0])
        if grupo == "Pacientes":
            return redirect("/home")
        elif grupo == "Doctores":
            basehtml = 'bases/basedentista.html'
            if request.method == "POST":
                form = forms.doc_tratamientos_pacientes(request.user, request.POST)
                if form.is_valid():
                    cur = connection.cursor()
                    id_tratamiento_paciente = 0
                    tratamiento = request.POST.get('Tratamientos')
                    doctor = usuario
                    paciente = request.POST.get('Pacientes')
                    citas = request.POST.get('Citas')
                    dia = request.POST.get('Dia')
                    hora = request.POST.get('Hora_Preferencia')
                    parsehora = hora[:hora.index(':')]
                    minutos = hora[hora.index(':') + 1:]
                    hora = int(parsehora) * 2
                    minutos = int(minutos) / 30
                    horafinal = int(hora + minutos)
                    print(horafinal)
                    cur.callproc('dientes.add_pkg.add_tratamiento_paciente',
                                 [id_tratamiento_paciente, tratamiento, paciente, doctor, citas, dia, horafinal])
                    cur.close()
                    return redirect('/home')
            else:
                form = forms.doc_tratamientos_pacientes(request.user)
        elif grupo == "Administrador":
            basehtml='bases/baseadministrador.html'
            if request.method == "POST":
                form = forms.admn_tratamientos_pacientes(request.user, request.POST)
                if form.is_valid():
                    cur = connection.cursor()
                    id_tratamiento_paciente = 0
                    tratamiento = request.POST.get('Tratamientos')
                    doctor = request.POST.get('Doctores')
                    paciente = request.POST.get('Pacientes')
                    citas = request.POST.get('Citas')
                    dia = request.POST.get('Dia')
                    hora = request.POST.get('Hora_Preferencia')
                    parsehora = hora[:hora.index(':')]
                    minutos = hora[hora.index(':') + 1:]
                    hora = int(parsehora) * 2
                    minutos = int(minutos) / 30
                    horafinal = int(hora + minutos)
                    print(horafinal)
                    cur.callproc('dientes.add_pkg.add_tratamiento_paciente',
                                 [id_tratamiento_paciente, tratamiento, paciente, doctor, citas, dia, horafinal])
                    cur.close()
                    return redirect('/home')
            else:
                form = forms.admn_tratamientos_pacientes(request.user)
        return render(request, 'asignar_tratamiento.html', {'form':form, 'usuario':usuario, 'basehtml':basehtml})

def verabonos(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
            basehtml = 'bases/basepaciente.html'
        else:
            grupo = str(groups[0])
            basehtml='bases/baseadministrador.html'
        if grupo == "Doctores":
            return redirect('/home')
        else:
            cur = connection.cursor()
            rawCursor = cur.connection.cursor()

            cur.callproc('dientes.get_pkg.get_abono', [usuario, grupo, rawCursor])
            res = rawCursor.fetchall()
            if not res:
                tablaFinal = None
            else:
                cur.callproc('dientes.get_pkg.get_abono', [usuario, grupo, rawCursor])
                tablaFinal = getTable(rawCursor, "tablaabonos")
                RequestConfig(request).configure(tablaFinal)

    return render(request,'verabonos.html', {'basehtml':basehtml, 'grupo':grupo, 'tablaFinal':tablaFinal})

def hacerpagos(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
        else:
            grupo = str(groups[0])
            basehtml='bases/baseadministrador.html'
        if grupo == "Doctores" or grupo == "Pacientes":
            return redirect('/home')
        else:
            if request.method == "POST":
                form = forms.forma_pagos(request.POST)
                if form.is_valid():
                    cur=connection.cursor()
                    rawCursor = cur.connection.cursor()
                    doctor = request.POST.get('Doctores')
                    paciente = request.POST.get('Pacientes')
                    tratamiento = request.POST.get('Tratamiento')
                    total = request.POST.get('Total')
                    tipopago = request.POST.get('Tipo_Pago')
                    pago = 0
                    cur.callproc('dientes.add_pkg.add_pagos',[pago, doctor, paciente, total, tipopago, tratamiento, rawCursor])
                    res = rawCursor.fetchall()
                    res = res[0]
                    res = res[0]
                    print(res)
                    cur.close()
                    messages.success(request, 'Tu cambio es: $'+str(res))
            else:
                form = forms.forma_pagos()
        return render(request, 'hacerpagos.html', {'form':form, 'basehtml':basehtml})

def home(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        userid = request.user.id
        group = request.user.groups.all()
        if not group:
            grupo = "Pacientes"
        else:
            grupo = str(group[0])
        if grupo == "Doctores":
            basehtml = 'bases/basedentista.html'
        elif grupo == "Administrador":
            basehtml = 'bases/baseadministrador.html'
        else:
            basehtml = 'bases/basepaciente.html'
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        cur.callproc('dientes.get_pkg.get_address_id', [userid, rawCursor])
        res = rawCursor.fetchall()
        if not res:
            return redirect('/update_user_info')
        else:
            cur.callproc('dientes.get_pkg.get_user', [userid, rawCursor])
            res = rawCursor.fetchall()
            for item in res:
                username = item[0]
                name = item[1]
                lastname = item[2]
            cur.callproc('dientes.get_pkg.get_user_home', [userid, rawCursor])
            res = rawCursor.fetchall()
            for item in res:
                name = item[0]
                email = item[1]
                calle = item[2]
                numero = item[3]
                ciudad = item[4]
                entidad = item[5]
                pais = item[6]
                celular = item[7]
                sexo = item[8]
                tipo_sangre = item[9]
            if grupo == "Doctores":
                cur.callproc('dientes.get_pkg.get_cita_cuenta_d', [rawCursor, userid])
                res = rawCursor.fetchall()
                if not res:
                    cuenta = 'NO'
                else:
                    for item in res:
                        cuenta = item[0]
                cur.callproc('dientes.get_pkg.get_pago_semana_d', [userid, rawCursor])
                res = rawCursor.fetchall()
                if not res:
                    pagos_d = 'NO'
                else:
                    for item in res:
                        pagos_d = item[0]
                return render(request, 'registro/Home.html',
                              {'pagos_d':pagos_d,'cuenta':cuenta,'sexo': sexo, 'correo': email, 'calle': calle, 'numero': numero, 'ciudad': ciudad,
                               'entidad': entidad, 'pais': pais, 'celular': celular, 'tipo_sangre': tipo_sangre,
                               'username': username, 'nombre': name, 'apellido': lastname, 'grupo': grupo,
                               'basehtml': basehtml})
            elif grupo == "Administrador":
                cur.callproc('dientes.get_pkg.get_pago_semana', [rawCursor])
                res = rawCursor.fetchall()
                if not res:
                    pagos_t = 'NO'
                else:
                    for item in res:
                        pagos_t = item[0]
                cur.callproc('dientes.get_pkg.get_cita_cuenta_a', [rawCursor])
                res = rawCursor.fetchall()
                if not res:
                    cuenta = 'NO'
                else:
                    for item in res:
                        cuenta = item[0]
                return render(request, 'registro/Home.html',
                              {'pagos_t':pagos_t,'cuenta':cuenta,'sexo': sexo, 'correo': email,
                               'calle': calle, 'numero': numero, 'ciudad': ciudad,
                               'entidad': entidad, 'pais': pais, 'celular': celular, 'tipo_sangre': tipo_sangre,
                               'username': username, 'nombre': name, 'apellido': lastname, 'grupo': grupo,
                               'basehtml': basehtml})
            else:
                cur.callproc('dientes.get_pkg.get_next_cita_p', [rawCursor, userid])
                res = rawCursor.fetchall()
                if not res:
                    name_dent = 'NO'
                    fecha = 'NO'
                    detalle = 'NO'
                else:
                    for item in res:
                        name_dent = item[1]
                        fecha = item[2]
                        detalle = item[3]
                cur.callproc('dientes.get_pkg.get_next_abono_p', [userid, rawCursor])
                res = rawCursor.fetchall()
                if not res:
                    nom_trat = 'NO'
                    fecha_ab = 'NO'
                    costo = 'NO'
                    pago = 'NO'
                else:
                    for item in res:
                        nom_trat = item[1]
                        fecha_ab = item[2]
                        costo = item[3]
                        pago = item[4]

                return render(request, 'registro/Home.html',
                              {'nom_trat': nom_trat, 'fecha_ab': fecha_ab, 'costo': costo, 'pago': pago,
                               'name_dent': name_dent, 'fecha': fecha, 'detalle': detalle, 'sexo': sexo,
                               'correo': email,
                               'calle': calle, 'numero': numero, 'ciudad': ciudad,
                               'entidad': entidad, 'pais': pais, 'celular': celular, 'tipo_sangre': tipo_sangre,
                               'username': username, 'nombre': name, 'apellido': lastname, 'grupo': grupo,
                               'basehtml': basehtml})

def lista_materiales(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
        else:
            grupo = str(groups[0])
        if grupo == "Pacientes":
            return redirect('/home')
        elif grupo == "Doctores":
            basehtml = 'bases/basedentista.html'
        elif grupo == "Administrador":
            basehtml = 'bases/baseadministrador.html'
    cur = connection.cursor()
    rawCursor=cur.connection.cursor()

    cur.callproc('dientes.get_pkg.get_material',[rawCursor])
    res = rawCursor.fetchall()
    if not res:
        tablaFinal = None
    else:
        cur.callproc('dientes.get_pkg.get_material', [rawCursor])
        tablaFinal = getTable(rawCursor, "tablamateriales")
        RequestConfig(request).configure(tablaFinal)
    return render(request, 'lista_materiales.html', {'materiales':tablaFinal, 'basehtml':basehtml})

def agregartipocambio(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
        else:
            grupo = str(groups[0])
            basehtml='bases/baseadministrador.html'
        if grupo == "Doctores" or grupo == "Pacientes":
            return redirect('/home')
        else:
            if request.method == "POST":
                form = forms.forma_tipo_cambio(request.POST)
                if form.is_valid():
                    cur=connection.cursor()
                    tipocambio = request.POST.get('Tipo_Cambio')
                    cur.callproc('dientes.add_pkg.add_cambio', [tipocambio])
                    cur.close()
                    return redirect('/home')
            else:
                form = forms.forma_tipo_cambio()
        return render(request, 'agregartipocambio.html', {'form':form, 'basehtml':basehtml})

def perfil(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        cur.callproc('dientes.get_pkg.get_address_id', [usuario, rawCursor])
        res = rawCursor.fetchall()
        if not res:
            return redirect('/update_user_info')
        else:
            if not groups:
                grupo = "Pacientes"
            else:
                grupo = str(groups[0])
            if grupo == "Doctores":
                basehtml = 'bases/basedentista.html'
            elif grupo == "Pacientes":
                basehtml = 'bases/basepaciente.html'
            elif grupo == "Administrador":
                basehtml = 'bases/baseadministrador.html'
        cur.callproc('dientes.get_pkg.get_user', [usuario, rawCursor])
        res = rawCursor.fetchall()
        for item in res:
            username = item[0]
            name = item[1]
            lastname = item[2]
        cur.callproc('dientes.get_pkg.get_user_home', [usuario, rawCursor])
        res = rawCursor.fetchall()
        for item in res:
            name = item[0]
            email = item[1]
            calle = item[2]
            numero = item[3]
            ciudad = item[4]
            entidad = item[5]
            pais = item[6]
            celular = item[7]
            sexo = item[8]
            tipo_sangre = item[9]

    return render(request, 'perfil.html',
                  {'sexo': sexo, 'correo': email, 'calle': calle, 'numero': numero, 'ciudad': ciudad,
                   'entidad': entidad, 'pais': pais, 'celular': celular, 'tipo_sangre': tipo_sangre,
                   'username': username, 'nombre': name, 'apellido': lastname, 'grupo': grupo, 'basehtml': basehtml})

def ver_pagos(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        cur.callproc('dientes.get_pkg.get_address_id', [usuario, rawCursor])
        res = rawCursor.fetchall()
        if not res:
            return redirect('/update_user_info')
        else:
            if not groups:
                grupo = "Pacientes"
            else:
                grupo = str(groups[0])
            if grupo == "Doctores":
                basehtml = 'bases/basedentista.html'
            elif grupo == "Pacientes":
                basehtml = 'bases/basepaciente.html'
            elif grupo == "Administrador":
                basehtml = 'bases/baseadministrador.html'
            cur = connection.cursor()
            rawCursor = cur.connection.cursor()
            cur.callproc('dientes.get_pkg.get_pago', [usuario, grupo, rawCursor])
            res = rawCursor.fetchall()
            if not res:
                tablaFinal = None
            else:
                cur.callproc('dientes.get_pkg.get_pago', [usuario, grupo, rawCursor])
                tablaFinal=getTable(rawCursor, "tablapagos")
                RequestConfig(request).configure(tablaFinal)
            return render(request, 'ver_pagos.html', {'pagos':tablaFinal, 'basehtml':basehtml})

def agregar_alergia(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        cur.callproc('dientes.get_pkg.get_address_id', [usuario, rawCursor])
        res = rawCursor.fetchall()
        if not res:
            return redirect('/update_user_info')
        else:
            if not groups:
                grupo = "Pacientes"
            else:
                grupo = str(groups[0])
            if grupo != "Administrador":
                return redirect('/home')
            else:
                basehtml = 'bases/baseadministrador.html'
                if request.method == "POST":
                    form = forms.agregar_alergia(request.POST)
                    if form.is_valid():
                        alergia = request.POST.get('Alergia')
                        cur = connection.cursor()
                        cur.callproc('dientes.add_pkg.add_alergia', [alergia])
                        cur.close()
                else:
                    form = forms.agregar_alergia()
                cur = connection.cursor()
                rawCursor = cur.connection.cursor()
                cur.callproc('dientes.get_pkg.get_alergia', [rawCursor])
                res = rawCursor.fetchall()
                if not res:
                    tablaFinal = None
                else:
                    cur.callproc('dientes.get_pkg.get_alergia', [rawCursor])
                    cur.close()
                    tablaFinal = getTable(rawCursor, 'tablaalergia')
                    RequestConfig(request).configure(tablaFinal)

                return render(request, 'agregar_alergia.html', {'form':form, 'basehtml':basehtml, 'alergias':tablaFinal})

def actualizar_historial(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        cur.callproc('dientes.get_pkg.get_address_id', [usuario, rawCursor])
        res = rawCursor.fetchall()
        if not res:
            return redirect('/update_user_info')
        else:
            if not groups:
                grupo = "Pacientes"
            else:
                grupo = str(groups[0])
            if grupo == "Doctores":
                return redirect('/home')
            elif grupo == "Pacientes":
                basehtml = 'bases/basepaciente.html'
                if request.method == "POST":
                    form = forms.alergia_paciente(request.POST)
                    form2 = forms.enfermedad_paciente(request.POST)
                    if form.is_valid() and form2.is_valid():
                        alergia = form.cleaned_data.get('Alergia')
                        enfermedad = form2.cleaned_data.get('Enfermedad')
                        paciente = request.user.id
                        cur = connection.cursor()
                        for item in alergia:
                            cur.callproc('dientes.add_pkg.add_paciente_alergia', [paciente, item])
                        for item in enfermedad:
                            cur.callproc('dientes.add_pkg.add_paciente_enfermedad', [paciente,item])
                        cur.close()
                        return redirect('/home')
                else:
                    form = forms.alergia_paciente()
                    form2 = forms.enfermedad_paciente()
            elif grupo == "Administrador":
                basehtml = 'bases/baseadministrador.html'
                if request.method == "POST":
                    form = forms.alergia_paciente_admn(request.POST)
                    form2 = forms.enfermedad_paciente_admn(request.POST)
                    if form.is_valid() and form2.is_valid():
                        alergia = form.cleaned_data.get('Alergia')
                        paciente = request.POST.get('Pacientes')
                        enfermedad = form2.cleaned_data.get('Enfermedad')
                        cur = connection.cursor()
                        for item in alergia:
                            cur.callproc('dientes.add_pkg.add_paciente_alergia', [paciente, item])
                        for item in enfermedad:
                            cur.callproc('dientes.add_pkg.add_paciente_enfermedad', [paciente,item])
                        cur.close()
                        return redirect('/home')
                else:
                    form = forms.alergia_paciente_admn()
                    form2= forms.enfermedad_paciente_admn()
            return render(request, 'alergia_paciente.html', {'form':form, 'form2':form2, 'basehtml':basehtml})

def paciente_perfil(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
        else:
            grupo = str(groups[0])
        if grupo == "Pacientes":
            return redirect('/home')
        elif grupo == "Doctores":
            basehtml = 'bases/basedentista.html'
        elif grupo == "Administrador":
            basehtml = 'bases/baseadministrador.html'
        return render(request, 'perfilpaciente.html', {'basehtml':basehtml})

def tratamiento_asignado(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        cur.callproc('dientes.get_pkg.get_address_id', [usuario, rawCursor])
        res = rawCursor.fetchall()
        if not res:
            return redirect('/update_user_info')
        else:
            if not groups:
                grupo = "Pacientes"
            else:
                grupo = str(groups[0])
            if grupo != "Pacientes":
                return redirect('/home')
            else:
                basehtml = 'bases/basepaciente.html'
            cur = connection.cursor()
            rawCursor = cur.connection.cursor()
            cur.callproc('dientes.get_pkg.get_tratamiento_paciente', [rawCursor, usuario])
            res = rawCursor.fetchall()
            if not res:
                tablaFinal = None
            else:
                cur.callproc('dientes.get_pkg.get_tratamiento_paciente', [rawCursor, usuario])
                tablaFinal = getTable(rawCursor, "tablatratamientos")
                RequestConfig(request).configure(tablaFinal)
            return render(request, 'tratamiento_asignado.html', {'basehtml':basehtml, 'tabla':tablaFinal})
@csrf_exempt
def search_ajax(request):
    cur = connection.cursor()
    rawCursor = cur.connection.cursor()
    #res = ''
    if request.POST.get('tag') == 'getstate':
        id_pais = request.POST.get('pais')
        cur.callproc('dientes.get_pkg.get_estados', [id_pais, rawCursor])
        res=rawCursor.fetchall()
        cur.close()
    elif request.POST.get('tag') == 'getcity':
        id_estado = request.POST.get('estado')
        cur.callproc('dientes.get_pkg.get_ciudades', [id_estado, rawCursor])
        res = rawCursor.fetchall()
        cur.close()
    elif request.POST.get('tag') == 'populateuser':
        usuario = request.user.id
        cur.callproc('dientes.get_pkg.get_user_info', [usuario, rawCursor])
        res = rawCursor.fetchall()
        cur.close()
    elif request.POST.get('tag') == "gethorario":
        usuario = request.POST.get('usuario')
        cur.callproc('dientes.get_pkg.get_horario_doc', [usuario, rawCursor])
        res = rawCursor.fetchall()
        cur.close()
    elif request.POST.get('tag') == 'dynamichorarios':
        doctor = request.POST.get('doctor')
        dia = request.POST.get('dia')
        cur.callproc('dientes.get_pkg.get_horario_dia', [doctor, dia, rawCursor])
        res=dictfetchall(rawCursor)
        res = res[0]
        res = res[dia.upper()]
        cur.close()
    elif request.POST.get('tag') == 'aceptarcita':
        citaid = request.POST.get('citasids')
        values = [int(x) for x in citaid.split(',') if x]
        for item in values:
            cur.callproc('dientes.edit_pkg.edit_cita_aceptar', [item])
    elif request.POST.get('tag') == 'gettreatmentcost':
        cur.callproc('dientes.get_pkg.get_tratamientos', [rawCursor])
        res=rawCursor.fetchall()
        res2=[]
        for item in res:
            res2.append((item[0],item[3]))
        res = res2
        cur.close()
    elif request.POST.get('tag') == 'populatecita':
        cita = request.POST.get('cita')
        cur.callproc('dientes.get_pkg.get_cita_with_id', [rawCursor, cita])
        res = rawCursor.fetchall()
        cur.close()
    elif request.POST.get('tag') == 'pagopaciente':
        doctor = request.POST.get('doctor')
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()

        cur.callproc('dientes.get_pkg.get_pacientes_doctor', [doctor, rawCursor])
        res = rawCursor.fetchall()
        cur.close()
    elif request.POST.get('tag') == 'pagotratamiento':
        paciente = request.POST.get('paciente')
        cur.callproc('dientes.get_pkg.get_tratamiento_paciente', [rawCursor, paciente])
        res = rawCursor.fetchall()
        cur.close()
    elif request.POST.get('tag') == 'populateperfil':
        paciente = request.POST.get('paciente')
        res=[]
        cur.callproc('dientes.get_pkg.get_user', [paciente, rawCursor])
        res2 = rawCursor.fetchall()
        res2=res2[0]
        for item in res2:
            res.append(item)
        cur.callproc('dientes.get_pkg.get_user_home', [paciente, rawCursor])
        res2 = rawCursor.fetchall()
        res2=res2[0]
        for item in res2:
            res.append(item)
    elif request.POST.get('tag') == 'tablaalergia':
        paciente = request.POST.get('paciente')
        cur.callproc('dientes.get_pkg.get_alergia_p', [rawCursor, paciente])
        res2 = rawCursor.fetchall()
        res=[]
        for item in res2:
            res.append(item[1])
    elif request.POST.get('tag') == 'tablatratamientos':
        paciente = request.POST.get('paciente')
        cur.callproc('dientes.get_pkg.get_tratamiento_paciente', [rawCursor, paciente])
        res = rawCursor.fetchall()
    elif request.POST.get('tag') == 'tablaenfermedades':
        paciente = request.POST.get('paciente')
        cur.callproc('dientes.get_pkg.get_enfermedad_p', [rawCursor, paciente])
        res2 = rawCursor.fetchall()
        print(res2)
        res = []
        for item in res2:
            res.append(item[0])
    elif request.POST.get('tag') == "deletecita":
        cita = request.POST.get('idcita')
        cur.callproc('dientes.delete_pkg.delete_cita', [cita])
        res=''
    elif request.POST.get('tag') == "deletetreat":
        tratamiento = request.POST.get('idtreat')
        cur.callproc('dientes.delete_pkg.delete_tratamiento_paciente', [tratamiento])
        res=''
    return HttpResponse(json.dumps(res))

    #return render(request,'search_ajax.html')

def hoy_citas (request):
    def __init__(self, *args, **kwargs):
        super(todas_citas, self).__init__(*args, **kwargs)
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
        else:
            grupo = str(groups[0])
        cur = connection.cursor()
        rawCursor = cur.connection.cursor()
        if grupo == "Doctores":
            basehtml = 'bases/basedentista.html'
            proc = 'dientes.get_pkg.get_cita_today'
            cur.callproc(proc, [rawCursor])
        elif grupo == "Pacientes":
            basehtml = 'bases/basepaciente.html'
            return redirect('/home')
        elif grupo == "Administrador":
            basehtml = 'bases/baseadministrador.html'
            proc = 'dientes.get_pkg.get_cita_today'
            cur.callproc(proc, [rawCursor])
        res = rawCursor.fetchall()
        if not res:
            citas = None
            return render(request, 'hoy_citas.html', {'citas':citas,'basehtml':basehtml, 'usuario':usuario, 'grupo':grupo})
        else:
            if grupo =="Administrador":
                cur.callproc(proc, [rawCursor])
            else:
                cur.callproc(proc, [rawCursor, usuario])
            tablaFinal = getTable(rawCursor, "tablacitas")
            RequestConfig(request).configure(tablaFinal)
        return render(request, 'hoy_citas.html', {'citas':tablaFinal, 'basehtml':basehtml, 'usuario':usuario, 'grupo':grupo})

def nuevo_material(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        usuario = request.user.id
        groups = request.user.groups.all()
        if not groups:
            grupo = "Pacientes"
        else:
            grupo = str(groups[0])
            basehtml='bases/baseadministrador.html'
        if grupo == "Pacientes" and grupo=="Doctores":
            return redirect('/home')
        else:
            if request.method == "POST":
                form = forms.agregar_material(request.POST)
                if form.is_valid():
                    cur=connection.cursor()
                    material = request.POST.get('Material')
                    cur.callproc('dientes.add_pkg.add_material', [material])
                    cur.close()
                    return redirect('/home')
            else:
                form = forms.agregar_material()
        return render(request, 'nuevo_material.html', {'form':form, 'basehtml':basehtml})