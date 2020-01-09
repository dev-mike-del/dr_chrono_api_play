from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

import views


urlpatterns = [
	url(r'^patient/(?P<id>[\w-]+)/$', views.Patient.as_view(), name='patient'),
	url(r'^patient_update/(?P<id>[\w-]+)/$', views.PatientUpdate.as_view(), name='patient_update'),
	url(r'^patients/$', views.Patients.as_view(), name='patients'),
    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='setup'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^appointments/$', views.Appointments.as_view(), name='appointments'),
    url(r'^appointment_search/$', views.AppointmentSearch.as_view(), name='appointment_search'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]