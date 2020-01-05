import datetime
from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.urls import reverse
from django.shortcuts import render
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_save
from notifications.signals import notify
from django.db.models import Q

from django.utils import timezone

class DefaultGroup(Group):
    def get_default(self):
        return 3

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_PI = models.BooleanField("Are you the Primary Investigator?", default=False)

    
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    groupname = instance.submitting_group.name
    return '{0}/{1}'.format(''.join(filter(str.isalnum, groupname)), filename)
    #return '{0}/{1}'.format(groupname, filename)
    
class Patient(models.Model):
    
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patient_dob = models.DateField("Date of Birth") 
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'Other'
    sex_choices = ((MALE, 'M'), (FEMALE, 'F'), (OTHER, 'Other'))
    patient_sex = models.CharField(choices=sex_choices, max_length=5)  
    transplant_date = models.DateField()
    creatinine_baseline = models.FloatField()
    submitting_group = models.ForeignKey(Group, on_delete=DefaultGroup.get_default)
    submitting_user = models.ForeignKey(User, on_delete=DefaultGroup.get_default)
    no_immuno = 'None'
    TORi = 'TORi'
    CNI = 'CNI'
    immuno_choices = ((TORi, 'TORi'), (CNI, 'CNI'), (no_immuno, 'None'))
    immuno_used = models.CharField(choices=immuno_choices, max_length = 4, default = no_immuno)
    drug_name = models.CharField(max_length=100, default ='')
    positive = 'Positive'
    negative = 'Negative'
    dsa_choices = ((positive, 'Positive'), (negative, 'Negative'))
    dsa = models.CharField(choices=dsa_choices, max_length = 8, default = negative)
    ns_antibody = models.CharField(max_length=100)
    alloantibody_details = models.CharField(max_length=100, default='')

    #Other Risk Factors

    DSA_RF = models.BooleanField("DSA", default=False)
    Previous_Rejection = models.BooleanField("Previous Rejection", default=False)
    Second_Transplant = models.BooleanField("Second Transplant", default=False)
    CNITac_Sensitivity = models.BooleanField("CNI/Tacrolimus sensitivity", default=False)

    misc_info_1 = models.TextField(default='')
    misc_info_2 = models.TextField(default='')
    graft_lost = models.BooleanField(default=0)
    deceased = models.BooleanField("Deceased?")
    
    consent = models.FileField(upload_to=user_directory_path, default='')
    
    
    
    def __str__(self):
        ptdob = self.patient_dob
        return self.last_name + ", " + self.first_name + ": " + ptdob.strftime('%Y-%m-%d')
    
    def get_group_Patients(self, groupid):
        group_Patients = Patient.objects.filter(submitting_group = groupid)
        return group_Patients
    
    def get_absolute_url(self):
        return reverse('samples:create-patient')
    
class PatientForm(ModelForm):

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'style':'width:25%'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'style':'width:25%'}))
    
    patient_dob = forms.DateField(label="Patient Date of Birth", widget=forms.DateInput(attrs={'class':'form-control', 'style':'width:25%'}))
    patient_sex = forms.ChoiceField(choices=Patient.sex_choices, widget=forms.Select(attrs={'class':'form-control', 'style':'width:25%'}))
    transplant_date = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control', 'style':'width:25%'}))
    creatinine_baseline = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control', 'style':'width:25%'}))
    immuno_used = forms.ChoiceField(choices=Patient.immuno_choices, widget=forms.RadioSelect(attrs={'class':'list-inline'}), label='Maintenance Immunosuppression')
    drug_name = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'style':'width:50%'}),label='Immunosuppressant Drugs Used (please separate with commas)')
    dsa = forms.ChoiceField(choices=Patient.dsa_choices, widget=forms.RadioSelect(attrs={'class':'list-inline'}), label='DSA status')
    ns_antibody = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'style':'width:50%'}),label='Other Non-specific antibodies (please separate with commas)')
    alloantibody_details = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'style':'width:50%'}))
    misc_info_1 = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'style':'width:50%'}))
    misc_info_2 = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'style':'width:50%'}))

    
    DSA_RF = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={}))
    Previous_Rejection = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={}))
    Second_Transplant = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={}))
    CNITac_Sensitivity = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={}))
    graft_lost = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={})) 
    deceased = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={}))
    consent = forms.FileField()
    
    class Meta:
        model = Patient
        fields = ('first_name', 'last_name', 'patient_dob', 'patient_sex', \
                'transplant_date', 'creatinine_baseline', 'immuno_used', 'drug_name', 'dsa', 'ns_antibody', \
                'DSA_RF', 'Previous_Rejection', 'Second_Transplant', 'CNITac_Sensitivity', \
                'alloantibody_details', 'misc_info_1', 'misc_info_2', 'graft_lost', 'deceased', 'consent')
    
    def clean(self, **kwargs):
        cleaned_data = super().clean()
        pdob = cleaned_data.get("patient_dob")
        
        #print(self.patient_id2)
        #sample_patient = Patient.objects.get(id=self.patient_id2)
        if pdob < datetime.date(1920, 1, 1):
            raise forms.ValidationError("Patient is too old, choose a date after 1/1/1920")
         
        tdate = cleaned_data.get("transplant_date")
        if tdate < pdob:
            raise forms.ValidationError("Transplant can not occur prior to patient's date of birth")
            
        
class sample(models.Model):
    #sample_dob = models.DateField("Sample Date of Birth") 
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    date_of_sample_collection = models.DateField()
    creatinine_current = models.FloatField()
    eGFR = models.FloatField()
    immunosuppression = models.FloatField()

    ACUTEREJECTION = 'Acute Rejection'
    BORDERLINE = 'Borderline'
    CHRONICREJECTION = 'Chronic Rejection'
    C4D = 'C4d'

    reason_choices = ((ACUTEREJECTION, 'Acute Rejection'), (BORDERLINE, 'Borderline'), \
                        (CHRONICREJECTION, 'Chronic Rejection'), (C4D, 'C4d'))
    reason_for_biopsy =  models.CharField(choices=reason_choices, max_length=17)
    biopsy_result = models.TextField()
    CXCL9_level = models.FloatField(default=0)
    CXCL10_level = models.FloatField(default=0)
    vegfa_level = models.FloatField(default=0)
    ccl2_level = models.FloatField(default=0)
    
    

    DRAFT = 'Draft'
    SUBMITTED = 'Submitted'
    RECEIVED = 'Received'
    TESTED = 'Tested'
    INSUFFICIENT = 'Insufficient'
    status_choices = ((DRAFT, 'Draft'), (SUBMITTED, 'Submitted'), \
                        (RECEIVED, 'Received'), (TESTED, 'Tested'), \
                        (INSUFFICIENT, 'Insufficient'))
    
    
    status_choices_university = ((DRAFT, 'Draft'), (SUBMITTED, 'Submitted'), \
                                    (INSUFFICIENT, 'Insufficient'))
                                    
    sample_status =  models.CharField(choices=status_choices, max_length=12)
    repeat_assay = models.BooleanField("Repeat Assay", default=False)
    medication_change = models.BooleanField("Medication Change", default=False)
    biopsy = models.BooleanField("biopsy", default=False)
    injury_risk = models.TextField(default='')
    submitting_group = models.ForeignKey(Group, on_delete=DefaultGroup.get_default)
    
    submitting_user = models.ForeignKey(User, on_delete=DefaultGroup.get_default)
    
    def __str__(self):
        return str(self.id)

    def get_group_samples(groupid):
        group_samples = sample.objects.filter(submitting_group = groupid)
        return group_samples
        
    def get_patient_samples(patientid):
        patient_samples = sample.objects.filter(patient = patientid)
        return patient_samples
        
    def get_absolute_url(self):
        return reverse('samples:sample-edit', kwargs={'pk': self.sample_id})
    
    def get_childrens_samples():
        pending_samples = sample.objects.filter(Q(sample_status__in=['Submitted', 'Received', 'Tested', 'Insufficient']))
        return pending_samples
        
    def export_data(groupid):
        # criteria1 = Q(sample_status__in=['Tested'])
        # criteria2 = Q(submitting_group = groupid)
        
        # export_samples = sample.objects.filter(criteria1 & criteria2)
        export_samples = [sample.objects.get(pk=1)]
        return export_samples
        
class SampleForm(ModelForm):
    
    date_of_sample_collection = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control', 'style':'width:25%'}))
    creatinine_current = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control', 'style':'width:25%'}))
    reason_for_biopsy = forms.ChoiceField(choices=sample.reason_choices, widget=forms.Select(attrs={'class':'form-control', 'style':'width:25%'}))
    biopsy_result = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'style':'width:50%'}),required=False)
    eGFR = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'style':'width:25%'}),label='eGFR')
    sample_status = forms.ChoiceField(choices=sample.status_choices_university, widget=forms.Select(attrs={'class':'form-control', 'style':'width:25%'}))
    
    class Meta:
        model = sample
        fields = ('date_of_sample_collection', 'creatinine_current', \
                    'reason_for_biopsy', 'biopsy_result', 'eGFR', 'sample_status')
        #widgets = {'sample_dob': forms.TextInput(attrs={'class':'form-field'}),} # 
    
    def __init__(self, *args, **kwargs):
        self.patient_id2 = kwargs.pop("patient_id", None)
        #print(self.patient_id2)
        super(SampleForm, self).__init__(*args, **kwargs)
        
    def clean(self, **kwargs):
        cleaned_data = super().clean()
        collect_date = cleaned_data.get("date_of_sample_collection")
        
        #print(self.patient_id2)
        sample_patient = Patient.objects.get(id=self.patient_id2)
        if collect_date < sample_patient.transplant_date:
            raise forms.ValidationError("Date of Sample Collection Can Not be Before Patient Transplant Date")
        
    #make the patient dropdown only show patients from the user's group
    '''
        user = kwargs.pop("user", None)
        if user is not None:
            self.fields["patient"].queryset = Patient.objects.filter(submittng_group_id=user.groups.all()[0].id)
        super(SampleForm, self).__init__(*args, **kwargs)
    
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())'''
    '''def save(self, sample=None):
        sample_data = super(SampleForm, self).save()
        if sample: 
            sample.id = sample
        sample.save()
        return sample'''


class ChildrensSampleForm(ModelForm):
    #sample_dob = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control', 'id':'disabledInput'}))
    date_of_sample_collection = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control', 'style':'width:25%'}), disabled=True)
    creatinine_current = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'style':'width:25%'}),  disabled=True)
    reason_for_biopsy = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'style':'width:50%'}), disabled=True, required=False)
    biopsy_result = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'style':'width:50%'}), disabled=True,required=False)
    eGFR = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'style':'width:25%'}),label='eGFR', disabled=True)
    #immunosuppression = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'style':'width:25%'}))
    CXCL9_level = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control', 'style':'width:25%'}), label='CXCL9')
    CXCL10_level = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control', 'style':'width:25%'}), label='CXCL10')
    vegfa_level = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control', 'style':'width:25%'}), label='VEGFA')
    ccl2_level = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control', 'style':'width:25%'}), label='CCL2')
    #injury_risk = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control', 'style':'width:25%'}))
    sample_status = forms.ChoiceField(choices=sample.status_choices, widget=forms.Select(attrs={'class':'form-control', 'style':'width:25%'}))
    
    
    
    class Meta:
        model = sample
        fields = ('date_of_sample_collection', 'creatinine_current', \
                    'reason_for_biopsy', 'biopsy_result', 'eGFR', 'CXCL9_level', 'CXCL10_level', 'vegfa_level', 'ccl2_level', 'sample_status') #
        #widgets = {'sample_dob': forms.TextInput(attrs={'class':'form-field'}),} # 
    
        
    #make the patient dropdown only show patients from the user's group
    '''def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        if user is not None:
            self.fields["patient"].queryset = Patient.objects.filter(submittng_group_id=user.groups.all()[0].id)
        super(ChildrensSampleForm, self).__init__(*args, **kwargs)
    
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())   '''     
    
'''class SampleAddForm(ModelForm):
    
    
    
    date_of_sample_collection = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control', 'style':'width:25%'}))
    creatinine_current = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control', 'style':'width:25%'}))
    reason_for_biopsy = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'style':'width:50%'}))
    biopsy_result = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'style':'width:50%'}),required=False)
    eGFR = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'style':'width:25%'}),label='eGFR')
    sample_status = forms.ChoiceField(choices=sample.status_choices_university, widget=forms.Select(attrs={'class':'form-control', 'style':'width:25%'}))
    #patient = forms.ModelChoiceField(queryset=Patient.objects.none(), widget=forms.Select(attrs={'class':'form-control', 'style':'width:25%'}))
    
    def __init__(self, *args, **kwargs):
        self.patient_id2 = kwargs.pop("patient_id", None)
        #print(self.patient_id2)
        super(SampleForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = sample
        fields = ('date_of_sample_collection', 'creatinine_current', \
                    'reason_for_biopsy', 'biopsy_result', 'eGFR', 'sample_status')
        #widgets = {'sample_dob': forms.TextInput(attrs={'class':'form-field'}),} # 
    
    def clean(self, **kwargs):
        cleaned_data = super().clean()
        collect_date = cleaned_data.get("date_of_sample_collection")
        
        #print(self.patient_id2)
        sample_patient = Patient.objects.get(id=self.patient_id2)
        if collect_date < sample_patient.transplant_date:
            raise forms.ValidationError("Date of Sample Collection Can Not be Before Patient Transplant Date")
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        if user is not None:
            super(SampleAddForm, self).__init__(*args, **kwargs)
            self.fields["patient"].queryset = Patient.objects.filter(submitting_group_id=user.groups.all()[0].id).filter(deceased=0).filter(graft_lost=0)'''
             
    #make the patient dropdown only show patients from the user's group
    
    
        

    
    
    