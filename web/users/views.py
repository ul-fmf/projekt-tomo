from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def mobile_app_token(request):
    if request.method == 'POST':
        print("HERE")
        print(request.POST)
        token = request.POST.get('token')
        if token:
            print("HERE")
            user = Token.objects.get(key=token).user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            print("HERE")
            login(request, user)
            print("HERE")
            return redirect('homepage')
    elif request.user.is_authenticated():
        token, _ = Token.objects.get_or_create(user=request.user)
        return JsonResponse({'token': token.key})
    raise PermissionDenied
