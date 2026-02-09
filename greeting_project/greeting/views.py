from django.shortcuts import render

def home(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        color = request.POST.get('color')
 
        if not name:
            return render(request, 'home.html', {'error':'Name required'})
 
        return render(request, 'result.html', {'name':name, 'color':color})
 
    return render(request, 'home.html')

def about(request):
    return render(request, 'greeting/about.html')