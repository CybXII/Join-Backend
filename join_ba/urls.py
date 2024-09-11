"""
URL configuration for join_ba project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from join.views import LoginView, BoardView, SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('join/login/', LoginView.as_view(), name='login'),
    path('join/signup/', SignUpView.as_view(), name='signup'),
    path('join/tasks/', BoardView.as_view(), name='tasks-list'),  # Für GET und POST ohne ID
    path('join/tasks/<int:id>/', BoardView.as_view(), name='tasks-detail'),  # Für PUT und DELETE mit ID
]