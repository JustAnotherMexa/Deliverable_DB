"""testing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include, url
#from registro import views
from testing import views
from django.contrib.auth.views import login, logout
from django.shortcuts import redirect

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register', include('registro.urls')),
    url(r'^login', login,{'template_name':'registro/login.html'}),
    url(r'^$', views.login_redirect),
    url(r'^logout/', logout, {'template_name': 'registro/logout.html'}),
    url(r'^update_user_info', views.update_user_info),
    url(r'^search_ajax/?$', views.search_ajax),
    url(r'^grupos', views.grupos_usuarios),
    url(r'^nueva_cita', views.new_app, name='nueva_cita'),
    url(r'^editar_cita', views.edit_app, name='editar_cita'),
    url(r'^todas_citas', views.todas_citas),
    url(r'^citas_confirmar', views.citas_confirmar),
    url(r'^horario', views.horario_vista),
    url(r'^pacientes', views.pacientes),
	url(r'^tratamientos', views.tratamientos),
    url(r'^asignar_tratamientos', views.asignar_tratamientos),
    url(r'^abonos', views.verabonos),
    url(r'^nuevo_pago', views.hacerpagos),
    url(r'^agregar_tipo_cambio', views.agregartipocambio),
    url(r'^home', views.home),
    url(r'^nuevo_tratamiento', views.nuevo_tratamiento),
    url(r'^materiales',views.lista_materiales),
    url(r'^perfil', views.perfil, name='perfil'),
    url(r'^ver_pagos', views.ver_pagos),
    url(r'^agregar_alergia', views.agregar_alergia),
    url(r'^actualizar_historial_medico', views.actualizar_historial),
    url(r'^paciente_perfil', views.paciente_perfil),
    url(r'^trat_asignados', views.tratamiento_asignado),
    url(r'^hoy_citas', views.hoy_citas),
    url(r'^nuevo_material', views.nuevo_material),
]
