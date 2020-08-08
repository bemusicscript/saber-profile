from django.shortcuts import render


class Index:
    def index(request):
        return render(request, "index.html")

    def about(request):
        return render(request, "about.html")


class Level:
    def index(request):
        return render(request, "level.html")
