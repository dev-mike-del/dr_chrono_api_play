from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from social_django.models import UserSocialAuth

from drchrono.endpoints import (
    DoctorEndpoint,
    PatientEndpoint,
    )
from drchrono import forms, models


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
        api = DoctorEndpoint(access_token)
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
        api = PatientEndpoint(access_token)
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


class Patient(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'patient.html'

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
        api = PatientEndpoint(access_token).fetch(self.kwargs['id'])
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return api

    def get_context_data(self, **kwargs):
        kwargs = super(Patient, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        patient = self.make_api_request()

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
        PatientEndpoint(access_token).update(
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