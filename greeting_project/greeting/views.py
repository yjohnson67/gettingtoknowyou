from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def home(request):
   if request.method == 'POST':
      name = request.POST.get('name')
      color = request.POST.get('color')

      if not name:
         return render(request, 'home.html', {'error':'Name required'})

      return render(request, 'result.html', {'name':name, 'color':color})

   return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

from django.http import JsonResponse
from django.utils.timezone import now
from .mongodb import scores_collection

@csrf_exempt
def save_test_score(request):
    result = scores_collection.insert_one({
        "player_name": "Test Player",
        "rocket_color": "#0000FF",
        "score": 25,
        "played_at": now().isoformat(),
    })

    return JsonResponse({
        "message": "Test score saved",
        "id": str(result.inserted_id),
    })