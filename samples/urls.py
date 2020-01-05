'''
These links are for the samples creating and editing
'''

from django.conf.urls import url
from django.urls import path
from .views import SampleDetailView

from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

from . import views

app_name = "samples"

urlpatterns =[
    #url(r'^login/$', auth_views.login, name='login'),
    path('', views.index, name='index'),
    #path('<int:pk>/', views.details, name='details'),
    path('<int:pk>/results', SampleDetailView.as_view(), name='sample-detail'),
    #path('active/', views.active, name='active'),
    path('<int:patient_id>/add/', views.addsample, name='add'),
    path('addpatient/', views.PatientCreate.as_view(), name='create-patient'),
    path('patients/', views.patients, name='patientshome'),
    path('<int:sample_id>/edit/', views.SampleUpdate.as_view(), name='sample-edit'),
    path('<int:sample_id>/childrensedit/', views.ChildrensSampleUpdate.as_view(), name='csample-edit'),
    path('patients/<int:patient_id>', views.SamplesbyPatient, name='patient-samples'),
    #path('export/', views.data_export, name='export'),
    path('pendingsamples/', views.forReview, name='pending-samples'),
    path('<int:pk>/deletesample/', views.SampleDelete.as_view(), name='delete-sample'),
    ]