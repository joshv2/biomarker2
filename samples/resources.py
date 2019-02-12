from import_export import resources
from .models import sample, Patient
from django.contrib.auth.models import User

class sampleResource(resources.ModelResource):
    class Meta:
        model = sample
        
    def get_queryset(self, **kwargs):
        groupid = self
        qs = sample.objects.filter(submitting_group = groupid)
        return qs