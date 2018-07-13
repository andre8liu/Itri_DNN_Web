from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
# Create your views here.



class viaView(View):
    #def index(request):
     #return render(request, 'via.html')


    def get(self,request):
        print("hey!!")
        testView = viaView()
        #return HttpResponse("<h1>Hello from python</h1>")
        return render(request, 'via.html', {'testView': testView} )

    def post(self,request):
        print(request.POST.get("data"))
        return HttpResponse("hey from post return")
