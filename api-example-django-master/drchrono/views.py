import collections

from datetime import date, datetime

from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from social_django.models import UserSocialAuth

from drchrono import endpoints, forms, models


def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data


class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


class DoctorWelcome(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_welcome.html'

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def make_api_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = self.get_token()
        api = endpoints.DoctorEndpoint(access_token)
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return next(api.list())

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        doctor_details = self.make_api_request()
        kwargs['doctor'] = doctor_details
        return kwargs

class Patients(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'patients.html'

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def make_api_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = self.get_token()
        api = endpoints.PatientEndpoint(access_token)
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return api.list()

    def get_context_data(self, **kwargs):
        kwargs = super(Patients, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        patients = self.make_api_request()
        kwargs['patients'] = patients
        return kwargs


class Patient(TemplateView, FormView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'patient.html'
    form_class = forms.AppointmentCheckIn

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def make_api_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = self.get_token()
        api = endpoints.PatientEndpoint(access_token).fetch(self.kwargs['id'])
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return api

    def get_context_data(self, **kwargs):
        kwargs = super(Patient, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        patient = self.make_api_request()
        patient = convert(patient)

        shared_fields = {}
        if models.Patient.objects.filter(patient_id=patient['id']).exists():
            for field in models.Patient._meta.get_fields():
                if field.name in patient:
                    if field.name == 'id':
                        shared_fields['patient_id'] = patient['id']
                    else:
                        shared_fields[field.name] = patient[field.name]
            models.Patient.objects.filter(
            patient_id=self.kwargs['id']).update(**shared_fields)
        else:
            for field in models.Patient._meta.get_fields():
                if field.name in patient:
                    if field.name == 'id':
                        shared_fields['patient_id'] = patient['id']
                    else:
                        shared_fields[field.name] = patient[field.name]
            models.Patient.objects.create(**shared_fields)

        kwargs['patient'] = patient
        return kwargs

    def form_valid(self, form):
        access_token = self.get_token()
        api_patient = self.make_api_request()
        api_appointments = endpoints.AppointmentEndpoint(access_token).list(date=date.today())
        appointment_number = ""
        for appointment in api_appointments:
            if appointment['patient'] == api_patient['id']:
                appointment_number = appointment['id']

        endpoints.AppointmentEndpoint(access_token).update(id=appointment_number, data={'status':'Arrived'})

        return HttpResponseRedirect(
          reverse(
              'appointment_search',
              )
          )


class PatientUpdate(TemplateView, FormView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'patient_update.html'
    form_class = forms.PatientForm

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        instance = models.Patient.objects.get(patient_id=self.kwargs['id'])
        initial = super(PatientUpdate, self).get_initial()

        initial['patient_id'] = instance.patient_id
        initial['first_name'] = instance.first_name
        initial['middle_name'] = instance.middle_name
        initial['last_name'] = instance.last_name
        initial['nick_name'] = instance.nick_name
        initial['social_security_number'] = instance.social_security_number
        initial['address'] = instance.address
        initial['zip_code'] = instance.zip_code
        initial['city'] = instance.city
        initial['state'] = instance.state
        initial['date_of_birth'] = instance.date_of_birth
        initial['home_phone'] = instance.home_phone
        initial['cell_phone'] = instance.cell_phone
        initial['office_phone'] = instance.office_phone
        initial['email'] = instance.email


        return initial

    def get_context_data(self, **kwargs):
        context = super(PatientUpdate, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        patient = models.Patient.objects.get(patient_id=self.kwargs['id'])
        context['patient'] = patient
        return context

    def form_valid(self, form):
        patient_form = form.save(commit=False)
        patient = models.Patient.objects.get(patient_id=self.kwargs['id'])

        access_token = self.get_token()
        data = patient_form.__dict__
        del data['_state']
        del data['id']
        clean_date = data
        endpoints.PatientEndpoint(access_token).update(
            id=self.kwargs['id'], 
            data=clean_date
            )

        models.Patient.objects.filter(
            patient_id=self.kwargs['id']).update(**patient_form.__dict__)

        return HttpResponseRedirect(
          reverse(
              'patient',
              kwargs={'id': patient_form.patient_id}
              )
          )


class Appointments(TemplateView, FormView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'appointments.html'
    form_class = forms.AppointmentInSession

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def make_api_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = self.get_token()
        api = endpoints.AppointmentEndpoint(access_token).list(date=date.today())
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return api

    def get_context_data(self, **kwargs):
        kwargs = super(Appointments, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        access_token = self.get_token()
        appointments = self.make_api_request()
        appointments_list = []

        for appointment in appointments:
            patient = endpoints.PatientEndpoint(access_token).fetch(
                appointment['patient'])
            appointment[u'first_name'] = patient[u'first_name']
            appointment[u'last_name'] = patient[u'last_name']
            appointment[u'updated_at'] = datetime.strptime(
                appointment[u'updated_at'], '%Y-%m-%dT%H:%M:%S')
            appointment = convert(appointment)
            appointments_list.append(appointment)

            shared_fields = {}
            if models.Patient.objects.filter(patient_id=patient['id']).exists():
                for field in models.Patient._meta.get_fields():
                    if field.name in patient:
                        if field.name == 'id':
                            shared_fields['patient_id'] = patient['id']
                        else:
                            shared_fields[field.name] = patient[field.name]
                models.Patient.objects.filter(
                patient_id=patient['id']).update(**shared_fields)
            else:
                for field in models.Patient._meta.get_fields():
                    if field.name in patient:
                        if field.name == 'id':
                            shared_fields['patient_id'] = patient['id']
                        else:
                            shared_fields[field.name] = patient[field.name]
                models.Patient.objects.create(**shared_fields)

        kwargs['appointments'] = appointments_list
        return kwargs

    def form_valid(self, form):
        if "submit" in self.request.POST:
            patient_id = self.request.POST.get('patient_id', None)
            appointment_id = self.request.POST.get('appointment_id', None)
            access_token = self.get_token()
            
            endpoints.AppointmentEndpoint(access_token).update(
                id=appointment_id, data={'status':'In Session'})

            return HttpResponseRedirect(
              reverse(
                  'appointments',
                  )
              )


def appointments(request):
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']
    appointments = endpoints.AppointmentEndpoint(access_token).list(date=date.today())
    appointments_list = []

    for appointment in appointments:
        patient = endpoints.PatientEndpoint(access_token).fetch(
            appointment['patient'])
        appointment[u'first_name'] = patient[u'first_name']
        appointment[u'last_name'] = patient[u'last_name']
        appointment[u'updated_at'] = datetime.strptime(
            appointment[u'updated_at'], '%Y-%m-%dT%H:%M:%S')
        appointment = convert(appointment)
        appointments_list.append(appointment)

        shared_fields = {}
        if models.Patient.objects.filter(patient_id=patient['id']).exists():
            for field in models.Patient._meta.get_fields():
                if field.name in patient:
                    if field.name == 'id':
                        shared_fields['patient_id'] = patient['id']
                    else:
                        shared_fields[field.name] = patient[field.name]
            models.Patient.objects.filter(
            patient_id=patient['id']).update(**shared_fields)
        else:
            for field in models.Patient._meta.get_fields():
                if field.name in patient:
                    if field.name == 'id':
                        shared_fields['patient_id'] = patient['id']
                    else:
                        shared_fields[field.name] = patient[field.name]
            models.Patient.objects.create(**shared_fields)

    appointments = appointments_list


    return render(request, 'appointments2.html', {'appointments': appointments})




class AppointmentSearch(Appointments, FormView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'appointment_search.html'
    form_class = forms.AppointmentSearchForm

    def form_valid(self, form):
        form = self.request.POST
        form = convert(form)
        access_token = self.get_token()
        appointments = self.make_api_request()
        appointments_list = []
        for appointment in appointments:
            api = endpoints.PatientEndpoint(access_token).fetch(appointment['patient'])
            appointment[u'first_name'] = api[u'first_name']
            appointment[u'last_name'] = api[u'last_name']
            appointment[u'social_security_number'] = api[u'social_security_number']
            appointment = convert(appointment)
            appointments_list.append(appointment)

        patient = models.Patient.objects.get(
            social_security_number=form['social_security_number'])

        for appointment in appointments_list:
            if (appointment['social_security_number'] == form['social_security_number'] and
                appointment['first_name'] == form['first_name'] and
                appointment['last_name'] == form['last_name']):
                return HttpResponseRedirect(reverse('patient',kwargs={
                    'id': patient.patient_id})
                )
                
        return HttpResponseRedirect(reverse('appointment_search'))

