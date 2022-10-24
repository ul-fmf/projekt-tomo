from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.authtoken.models import Token


@login_required
def mobile_app_token(request):
    token, _ = Token.objects.get_or_create(user=request.user)
    return JsonResponse({"token": token.key})
