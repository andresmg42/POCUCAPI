"""
URL configuration for pocuc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path,include
from surveysession.views import SurveysessionViewSet # Import view from the app
from rest_framework.routers import DefaultRouter
from visit.views import VisitViewSet
from category.views import CategoryViewSet
router = DefaultRouter()
router.register(r'surveysession', SurveysessionViewSet, basename='surveysession')
router.register(r'visit',VisitViewSet,basename='visit')
router.register(r'category',CategoryViewSet,basename='category')
urlpatterns = [
    path('admin/', admin.site.urls),
    path("category/", include("category.urls")),
    path("observer/", include("observer.urls")),
    path("option/", include("option.urls")),
    path("question/", include("question.urls")),
    path("response/", include("response.urls")),
    path("subcategory/", include("subcategory.urls")),
    path("survey/", include("survey.urls")),
    # path("surveysession/", include("surveysession.urls")),
    path("visit/", include("visit.urls")),
    path("zone/", include("zone.urls")),
    path('surveysession/', include('surveysession.urls')), 
    path('pocucstats/', include('pocucstats.urls')), 
    
]
