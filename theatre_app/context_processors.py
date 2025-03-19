from .models import Theatre_Profile

def theatre_list(request):
    return {'theatre_list': Theatre_Profile.objects.all()}
