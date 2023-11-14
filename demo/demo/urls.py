from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views
from users import views as user_views
from users.views import sell_stock

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('stock_data.html',views.stock_data_view,name='stock_data'),
    path('buy_stock.html', views.buy_stock, name='buy_stock'),
    path('users/success_page.html',views.success_page, name='success_page'),
    path('users/transaction_history,html', views.transaction_history, name='transaction_history'),
    path('sell_stock/', sell_stock, name='sell_stock'),
    path('stock_graph_symbol/<str:symbol>/<int:days>/', views.stock_graph_symbol, name='stock_graph_symbol'),
    path('error_page', views.error_page, name='error_page'),
    path('social-auth/', include('social_django.urls', namespace='social')),
 

    

]