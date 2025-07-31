from django.shortcuts import render

def home_view(request):
    """主页视图函数"""
    return render(request, 'home.html')