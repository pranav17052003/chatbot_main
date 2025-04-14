from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username
                    }
                })
            return JsonResponse({
                'success': False,
                'message': 'Invalid credentials'
            }, status=401)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON format'
            }, status=400)
            
    return JsonResponse({
        'success': False,
        'message': 'Only POST method allowed'
    }, status=405)

@csrf_exempt
@login_required
def logout_view(request):
    logout(request)
    return JsonResponse({
        'success': True,
        'message': 'Logout successful'
    })

@login_required
def check_auth(request):
    return JsonResponse({
        'success': True,
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username
        }
    })