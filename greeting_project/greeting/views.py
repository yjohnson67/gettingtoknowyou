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
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
 
from .mongodb import scores_collection
 
 
@csrf_exempt
def save_test_score(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "POST only"},
            status=405
        )
 
    try:
        data = json.loads(request.body)
 
        player_name = data.get("player_name")
        rocket_color = data.get("rocket_color")
        score = data.get("score")
 
        print("Received from Flutter:", data)
 
        result = scores_collection.insert_one({
            "player_name": player_name,
            "rocket_color": rocket_color,
            "score": score,
            "played_at": now().isoformat(),
        })
 
        return JsonResponse({
            "success": True,
            "inserted_id": str(result.inserted_id),
        })
 
    except Exception as e:
        print("SAVE ERROR:", str(e))
        return JsonResponse(
            {"success": False, "error": str(e)},
            status=500
        )