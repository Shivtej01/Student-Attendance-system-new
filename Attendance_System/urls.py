from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from api_v1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', views.login_choice, name='login'),
    path('accounts/student/login/', views.student_login, name='student_login'),
    path('accounts/admin/login/', views.admin_login, name='admin_login'),
    path('accounts/student/signup/', views.student_signup, name='student_signup'),
    path('accounts/admin/signup/', views.admin_signup, name='admin_signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('', include('api_v1.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
