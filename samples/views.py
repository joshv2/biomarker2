import datetime
from datetime import timedelta
from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.http import JsonResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from .models import SampleForm, PatientForm, ChildrensSampleForm
from .models import sample, Patient
from django.forms import ModelForm
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse, reverse_lazy
from djqscsv import render_to_csv_response
from django.db.models.signals import post_save
from notifications.signals import notify
from django.contrib.auth.models import Group



def homepage(request): #entrypage
    if request.user.is_authenticated:
        user = request.user
        #template = loader.get_template('samples/home.html')
        context = {'user' : user, 'notifications' : user.notifications.unread()}
    else:
        context = {'user' : '', 'notifications' : ''}
    return render(request, 'samples/home.html', context=context)

    
@login_required(login_url='/accounts/login/')  
def index(request): #entryway to samples
    user = request.user
    user_group = request.user.groups.all()[0].id
    #group_samples = sample.get_group_samples(user_group)
    #user.profile.is_PI:
    #if 3 != user_group:
    group_samples = sample.get_group_samples(user_group)
    for biosample in group_samples:
        if "Tested" == biosample.sample_status:
            biosample.link =  str(biosample.id) + '/results'
            biosample.link_text = "Results"
        elif biosample.sample_status in ("Submitted", "Insufficient"):
            biosample.link =  ''
            biosample.link_text = ""
        elif "Draft" == biosample.sample_status:
            biosample.link = str(biosample.id) + '/edit'
            biosample.link_text = "Edit"
    #context = {'user' : user, 'group_samples': group_samples}
    context = {'user' : user, 'group_samples': group_samples, 'group_id': user_group, 'notifications' : user.notifications.unread()}    
    '''elif 3 == user_group:
        pending_samples = sample.get_childrens_samples()
        for biosample in pending_samples:
            biosample.university = biosample.submitting_group.name
            if "Tested" == biosample.sample_status:
                biosample.link =  str(biosample.id) + '/results'
                biosample.link_text = "Results"
            elif biosample.sample_status in ("Submitted", "Received", "Insufficient"):
                biosample.link =  str(biosample.id) + '/childrensedit'
                biosample.link_text = "Add Results"
            elif biosample.sample_status in ("Consented") and 3 == biosample.submitting_group_id:
                biosample.link =  str(biosample.id) + '/edit'
                biosample.link_text = "Edit"
            
        context = {'user' : user, 'group_samples': pending_samples, 'group_id': user_group}'''        
    
    
    #return render(request, 'samples/active.html', context) 
    #context = {}
    return render(request, 'samples/sampleshome.html', context=context)

    
@login_required(login_url='/accounts/login/') 
def data_export(request):
    user_group = request.user.groups.all()[0].id
    qs = sample.objects.filter(submitting_group = user_group)
    return render_to_csv_response(qs)
    
@login_required(login_url='/accounts/login/')  
def patients(request): 
    user = request.user
    user_group = request.user.groups.all()[0].id
    #group_samples = sample.get_group_samples(user_group)
    #user.profile.is_PI:
    group_patients = Patient.get_group_Patients(user_group)
    
    context = {'user' : user, 'group_patients': group_patients, 'group_id': user_group, 'notifications' : user.notifications.unread()}
            
                
    
    
    #return render(request, 'samples/active.html', context) 
    #context = {}
    return render(request, 'samples/patientshome.html', context=context)


@login_required(login_url='/accounts/login/')  
def forReview(request):
    user = request.user
    user_group = request.user.groups.all()[0].id
    if 3 == user_group:
        pending_samples = sample.get_childrens_samples()
        for biosample in pending_samples:
            biosample.university = biosample.submitting_group.name
            if "Tested" == biosample.sample_status:
                biosample.link =  str(biosample.id) + '/results'
                biosample.link_text = "Results"
            elif biosample.sample_status in ("Submitted", "Received"):
                biosample.link =  str(biosample.id) + '/childrensedit'
                biosample.link_text = "Add Results"
            elif biosample.sample_status in ("Insufficient"):
                biosample.link =  ''
                biosample.link_text = ""
        context = {'user' : user, 'group_samples': pending_samples, 'group_id': user_group, 'notifications' : user.notifications.unread()}
    else:
        raise Http404("You are not authorized to view this page.")
        
    return render(request, 'samples/sampleshome.html', context=context)
    
    
@login_required(login_url='/accounts/login/')   
def addsample(request, **kwargs):
    
    if request.method == 'POST':
        form = SampleForm(patient_id=kwargs.get('patient_id'), data=request.POST)
        patientid=kwargs.get('patient_id')
        user=request.user
        patient = Patient.objects.get(pk=patientid)
        if form.is_valid():
            newsample = form.save(commit=False)
            
            #newsample.eGFR = 0
            newsample.immunosuppression = 0
            #newsample.biopsy_result = ''
            #newsample.protein4 = 0
            newsample.patient_id = kwargs.get('patient_id')
            newsample.submitting_group_id = request.user.groups.all()[0].id
            newsample.submitting_user_id = request.user.id
            newsample.save()
            return HttpResponseRedirect('/samples/patients/' + str(newsample.patient_id))
    else:
        #e = "New Form"
        patientid = kwargs.get('patient_id')
        patient = Patient.objects.get(pk=patientid)
        user=request.user
        form = SampleForm #(user=user)
    return render(request, 'samples/sampleadd.html', {'form': form, 'notifications' : user.notifications.unread(), 'patient' : patient}) #, 'content' : e
    
'''@login_required(login_url='/login/') 
def active(request):
    user_group = request.user.groups.all()[0].id
    group_samples = sample.get_group_samples(user_group)
    context = {'group_samples': group_samples}
    
    return render(request, 'samples/sampleshome.html', context)  ''' 

    
def SamplesbyPatient(request, patient_id, **kwargs):    
    template_name = 'samples/sampleshome.html'
    user = request.user
    user_group = request.user.groups.all()[0].id
    #patient_id = kwargs.get('patient_id')
    patient = Patient.objects.get(pk=patient_id)
    if patient.submitting_group_id == user_group:
        group_samples = sample.get_patient_samples(patient_id)
        for biosample in group_samples:
            if "Tested" == biosample.sample_status:
                biosample.link =  str(biosample.id) + '/results'
                biosample.link_text = "Results"
            elif biosample.sample_status in ("Submitted", "Insufficient"):
                biosample.link =  ''
                biosample.link_text = ""
            elif "Draft" == biosample.sample_status:
                biosample.link = str(biosample.id) + '/edit'
                biosample.link_text = "Edit"
        context = {'user' : user, 'group_samples': group_samples, 'patient': patient, 'notifications' : user.notifications.unread()}
        
    
    else:
        raise Http404("You are not authorized to view these samples.")
        
    return render(request, 'samples/sampleshome.html', context=context)
    
    '''def test_func(self):
        requestedPatient = Patient.objects.get(pk=self.kwargs['pk'])
        if requestedPatient.submitting_group_id == self.request.user.groups.all()[0].id:
            return True
        else:
            if self.request.user.is_authenticated:
                raise Http404("You are not authorized to view these samples." + str(requestedPatient.submitting_group))'''
    
            

class SampleDetailView(UserPassesTestMixin, LoginRequiredMixin, DetailView):

    model = sample
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['notifications'] = user.notifications.unread()
        
        
        #context.update(self.extra_context)
        return context

    def test_func(self):
        
        x = self.request.user.groups.all()[0].id
        requestedform = self.get_object()
        y = requestedform.submitting_group_id
        if (x == y and "Tested" == requestedform.sample_status) or (x == 3 and "Tested" == requestedform.sample_status):
            return True
        else:
            if self.request.user.is_authenticated:
                raise Http404("You are not authorized to edit this page" + str(x), str(y))



                
class PatientCreate(LoginRequiredMixin, CreateView):  
    model = Patient
    form_class = PatientForm
    template_name = 'samples/patientadd.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['notifications'] = user.notifications.unread()
        
        
        #context.update(self.extra_context)
        return context
    
    def form_valid(self, form):
        form.instance.submitting_user = self.request.user
        form.instance.submitting_group = self.request.user.groups.all()[0]
        form.instance.submitting_groupname = self.request.user.groups.all()[0].name
        #form.instance.nwewid = self.kwargs['pk']
        return super(PatientCreate, self).form_valid(form)
        
    def get_success_url(self):
        view_name = '/samples/patients/'
        return view_name
  
class SampleUpdate(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    
    #x = self.request.user.groups.all()[0].id
    model = sample
    form_class = SampleForm
    #form_class.fields["patient"].queryset = \
        #Patient.objects.filter(submittng_group_id=user.groups.all()[0].id)
        
    def get_object(self, queryset=None):
        obj, status = sample.objects.get_or_create(pk=self.kwargs['sample_id'])
        print(obj)
        return obj
    
    def get_context_data(self, **kwargs):
        #print(super().get_context_data(**kwargs))
        context = super().get_context_data(**kwargs)
        print(context)
        user = self.request.user
        context['notifications'] = user.notifications.unread()
        #context.update(self.extra_context)
        return context
        
    def test_func(self):
        
        x = self.request.user.groups.all()[0].id
        requestedform = self.get_object()
        print(requestedform.date_of_sample_collection)
        y = requestedform.submitting_group_id
        if x == y and requestedform.sample_status in ('Draft'):
            return True
        else:
            #if self.request.user.is_authenticated:
            raise Http404("You are not authorized to edit this sample" + str(x) + ', ' + str(y))
    
    def form_valid(self, form):
        #form.instance.submitting_user = self.request.user
        #notify.send(form.instance, recipient=Group.objects.get(id=3), verb='changed to ' + form.instance.sample_status)
        requestedform = self.get_object()
        print(requestedform)
        print(form)
        y = requestedform.submitting_group_id
        notify.send(form.instance, recipient=Group.objects.get(id=3), verb='changed to ',  description=form.instance.sample_status, action_object=sample.objects.get(pk=requestedform.id))
        return super().form_valid(form)
    
    
    def get_success_url(self):
        editedsample = sample.objects.get(pk=self.kwargs['sample_id'])
        view_name = '/samples/patients/' + str(editedsample.patient_id)
        return view_name
        #form_class.instance.submitting_user = self.request.user
        #super(SampleUpdate, self).save(form_class)
        
        
    #fields = SampleForm.Meta.fields
    #widgets = {'sample_dob': DateField(attrs={'class':'form-control'}),}
    template_name = 'samples/sampleedit.html'

class ChildrensSampleUpdate(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = sample
    form_class = ChildrensSampleForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['notifications'] = user.notifications.unread()
        
        
        #context.update(self.extra_context)
        return context
    
    def get_object(self, queryset=None):
        obj = sample.objects.get(pk=self.kwargs['sample_id'])
        print(obj)
        return obj
    

    def test_func(self):
        
        x = self.request.user.groups.all()[0].id
        requestedform = self.get_object()
        y = requestedform.submitting_group_id
        
        if 3 == x and requestedform.sample_status in ("Submitted", "Received", "Tested"):
            return True
        else:
            if self.request.user.is_authenticated:
                raise Http404("You are not authorized to edit this sample")    
    
    def check_values(self, CXCL9, CXCL10, VEGFA, CCL2):
        biomarkerresults = {'CXCL9' : '', 'CXCL10' : '', 'VEGFA' : '', 'CCL2' : ''}
        if CXCL9 > 30:
            biomarkerresults['CXCL9'] = 'High'
        else:
            biomarkerresults['CXCL9'] = 'Low'
        if CXCL10 > 15:
            biomarkerresults['CXCL10'] = 'High'
        else:
            biomarkerresults['CXCL10'] = 'Low'
        if VEGFA > 200:
            biomarkerresults['VEGFA'] = 'High'
        else:
            biomarkerresults['VEGFA'] = 'Low'
        if CCL2 > 245:
            biomarkerresults['CCL2'] = 'High'
        else:
            biomarkerresults['CCL2'] = 'Low'
        return biomarkerresults
    
    def form_valid(self, form):
        requestedform = self.get_object()
        biomarkersover = self.check_values(form.instance.CXCL9_level, form.instance.CXCL10_level, form.instance.vegfa_level, form.instance.ccl2_level)
        if biomarkersover == {'CXCL9': 'Low', 'CXCL10': 'Low', 'VEGFA': 'Low', 'CCL2': 'Low'}:
            form.instance.injury_risk = '<10%'
        if biomarkersover == {'CXCL9': 'High', 'CXCL10': 'High', 'VEGFA': 'High', 'CCL2': 'High'}:
            form.instance.injury_risk = '>90%'
        if biomarkersover == {'CXCL9': 'High', 'CXCL10': 'High', 'VEGFA': 'Low', 'CCL2': 'Low'} or \
            biomarkersover == {'CXCL9': 'High', 'CXCL10': 'High', 'VEGFA': 'Low', 'CCL2': 'High'} or \
            biomarkersover == {'CXCL9': 'High', 'CXCL10': 'High', 'VEGFA': 'High', 'CCL2': 'Low'}:
            form.instance.injury_risk = '>80%'
        if biomarkersover == {'CXCL9': 'High', 'CXCL10': 'Low', 'VEGFA': 'Low', 'CCL2': 'Low'} or \
            biomarkersover == {'CXCL9': 'High', 'CXCL10': 'Low', 'VEGFA': 'High', 'CCL2': 'Low'} or \
            biomarkersover == {'CXCL9': 'High', 'CXCL10': 'Low', 'VEGFA': 'Low', 'CCL2': 'High'} or \
            biomarkersover == {'CXCL9': 'High', 'CXCL10': 'Low', 'VEGFA': 'High', 'CCL2': 'High'} or \
            biomarkersover == {'CXCL9': 'Low', 'CXCL10': 'High', 'VEGFA': 'Low', 'CCL2': 'Low'} or \
            biomarkersover == {'CXCL9': 'Low', 'CXCL10': 'High', 'VEGFA': 'High', 'CCL2': 'Low'} or \
            biomarkersover == {'CXCL9': 'Low', 'CXCL10': 'High', 'VEGFA': 'Low', 'CCL2': 'High'} or \
            biomarkersover == {'CXCL9': 'Low', 'CXCL10': 'High', 'VEGFA': 'High', 'CCL2': 'High'}:
            form.instance.injury_risk = '>80%'
        if biomarkersover == {'CXCL9': 'Low', 'CXCL10': 'Low', 'VEGFA': 'High', 'CCL2': 'Low'} or \
            biomarkersover == {'CXCL9': 'Low', 'CXCL10': 'Low', 'VEGFA': 'Low', 'CCL2': 'High'}:
            form.instance.injury_risk = '50%'
        if biomarkersover == {'CXCL9': 'Low', 'CXCL10': 'Low', 'VEGFA': 'High', 'CCL2': 'High'}:
            form.instance.injury_risk = 'No risk asasigned.'
        print(biomarkersover)
        #print(form)
        print(form.instance.injury_risk)
        y = requestedform.submitting_group_id
        requestedform = self.get_object()
    
        x = requestedform.sample_status
        z = form.instance.sample_status
        if z != x:
            notify.send(form.instance, recipient=Group.objects.get(id=y), verb='changed to ',  description=form.instance.sample_status, action_object=sample.objects.get(pk=requestedform.id))
        
        redirect_url = '/samples/pendingsamples/'
        return super().form_valid(form)
    
    '''def form_valid(self, form):
        requestedform = self.get_object()
        #
        biomarkersover = self.check_values(form.instance.CXCL9_level, form.instance.CXCL10_level, form.instance.vegfa_level, form.instance.ccl2_level)
        return super().form_valid(form)'''
    '''form.instance.injury_risk = '<10%'
    if all(value == 'Low' for value in biomarkersover):
        form.instance.injury_risk = '<10%'
    elif biomarkersover['VEGFA'] == 'High' or biomarkersover['CCL2'] == 'High':
        form.instance.injury_risk = '50%'
    elif biomarkersover['CXCL9'] == 'High' and biomarkersover['CXCL10'] == 'High':
        form.instance.injury_risk = '>80%'
    elif all(value == 'High' for value in biomarkersover):
        form.instance.injury_risk = '>90%'
    else:
        form.instance.injury_risk = 'Undetermined'
    requestedform = self.get_object()
    y = requestedform.submitting_group_id
    x = requestedform.sample_status
    z = form.instance.sample_status
    if z != x:
        notify.send(form.instance, recipient=Group.objects.get(id=y), verb='changed to ',  description=form.instance.sample_status, action_object=sample.objects.get(pk=requestedform.id))'''
        #form.instance.save()
        #return super(ChildrensSampleUpdate, self).form_valid(form)
        #return super().form_valid(form)
        
    def get_success_url(self):
        view_name = '/samples/pendingsamples/'
        return view_name
    
    '''def check_values(self, CXCL9, CXCL10, VEGFA, CCL2):
        biomarkerresults = {'CXCL9' : '', 'CXCL10' : '', 'VEGFA' : '', 'CCL2' : ''}
        if CXCL9 > 30:
            biomarkerresults['CXCL9'] = 'High'
        else:
            biomarkerresults['CXCL9'] = 'Low'
        if CXCL10 > 15:
            biomarkerresults['CXCL10'] = 'High'
        else:
            biomarkerresults['CXCL10'] = 'Low'
        if VEGFA > 200:
            biomarkerresults['VEGFA'] = 'High'
        else:
            biomarkerresults['VEGFA'] = 'Low'
        if CCL2 > 245:
            biomarkerresults['CCL2'] = 'High'
        else:
            biomarkerresults['CCL2'] = 'Low'
        return biomarkerresults'''
        
    
    
    '''def form_valid(self, form):
        #form.instance.submitting_user = self.request.user
        requestedform = self.get_object()
        y = requestedform.submitting_group_id
        notify.send(form.instance, recipient=Group.objects.get(id=y), verb='changed to ' + form.instance.sample_status)
        return super().form_valid(form)'''
    
    template_name = 'samples/sampleedit.html'
    
class SampleDelete(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = sample
    #success_url = '/samples/patients/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['notifications'] = user.notifications.unread()
        
        
        #context.update(self.extra_context)
        return context
    
    def get_object(self, queryset=None):
        obj = sample.objects.get(pk=self.kwargs['pk'])
        print(obj)
        return obj
        
    def get_success_url(self):
        requestedform = self.get_object()
        view_name = '/samples/patients/' + str(requestedform.patient_id)
        return view_name
        
    def test_func(self):
        
        x = self.request.user.groups.all()[0].id
        requestedform = self.get_object()
        y = requestedform.submitting_group_id
        if x == y:
            return True
        else:
            #if self.request.user.is_authenticated:
            raise Http404("You are not authorized to delete this sample" + str(x) + ', ' + str(y))