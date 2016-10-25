"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

import docs.urls
import ovp_users.urls
import ovp_projects.urls
import ovp_uploads.urls
import ovp_projects.urls

urlpatterns = [
    # Admin panel
    url(r'^admin/', admin.site.urls),

    # API Documentation
    url(r'^docs/', include(docs.urls)),

    # User module endpoints
    url(r'^', include(ovp_users.urls)),

    # Project module endpoints
    url(r'^', include(ovp_projects.urls)),

    # Upload module endpoints
    url(r'^', include(ovp_uploads.urls))
]
