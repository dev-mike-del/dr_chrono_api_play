from django.db import models


class Patient(models.Model):
    patient_id = models.PositiveIntegerField()
    first_name = models.CharField(
        max_length=300, 
        null=True,
        blank=True
        )
    middle_name = models.CharField(
        max_length=300, 
        null=True,
        blank=True
        )
    last_name = models.CharField(
        max_length=300, 
        null=True,
        blank=True
        )
    nick_name = models.CharField(
        max_length=300, 
        null=True,
        blank=True
        )
    social_security_number = models.CharField(
        max_length=300, 
        null=True,
        blank=True
        )
    address = models.TextField()
    zip_code = models.PositiveSmallIntegerField()
    city = models.CharField(
        max_length=300, 
        null=True,
        blank=True
        ) 
    state = models.CharField(
        max_length=300, 
        null=True,
        blank=True
        )
    date_of_birth = models.DateField()
    home_phone = models.CharField(
        max_length=300, 
        null=True,
        blank=True
        )
    cell_phone = models.CharField(
        max_length=300, 
        null=True,
        blank=True
        )
    office_phone = models.CharField(
        max_length=300, 
        null=True,
        blank=True
        )
    email = models.EmailField(
        blank=True)
    # patient_photo = models.TextField()

    # race: indian
    # ethnicity: hispanic
    # gender: Male
    # preferred_language: eng
    
    # employer_zip_code = models.PositiveSmallIntegerField()
    # employer = models.CharField(max_length=300)
    # employer_address = models.TextField()
    # employer_city = models.CharField(max_length=300)
    # employer_state = models.CharField(max_length=300)

    # emergency_contact_name = models.CharField(max_length=300)
    # emergency_contact_phone = models.CharField(max_length=300)
    # emergency_contact_relation = models.CharField(max_length=300)
    # responsible_party_name = models.CharField(max_length=300)
    # responsible_party_phone = models.CharField(max_length=300)
    # responsible_party_relation = models.CharField(max_length=300)
    # responsible_party_email = models.EmailField()

    
    # offices = [273340]
    # doctor = 257154
    # primary_care_physician = models.CharField(max_length=300)
    # default_pharmacy = 5644631

    # chart_id = models.CharField(max_length=300)
    # patient_status = A
    # date_of_first_appointment = 2020-01-06
    # date_of_last_appointment = 2020-01-06
    # patient_payment_profile = Cash
    # copay =
    
    # updated_at = 2020-01-04T12 =13 =00
    # referring_source = None
    
    # disable_sms_messages = models.BooleanField()
    
    
    

