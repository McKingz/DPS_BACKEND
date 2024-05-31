from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from mlm.views import (UserDetailView, RegisterView, LoginView, ReferredUsersView, 
                       RecentActivityList, ProfileView, UserDetailUpdateView, CommissionListView)
from mlm.views import get_referral_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/', UserDetailView.as_view(), name='user_detail'),
    path('api/user/update', UserDetailUpdateView.as_view(), name='user-detail-update'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/referred-users/', ReferredUsersView.as_view(), name='referred_users'),
    path('api/recent-activity/', RecentActivityList.as_view(), name='recent_activity'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/referral-url/', get_referral_url, name='referral_url'),
    path('api/commissions/', CommissionListView.as_view(), name='commissions'),
    path('api/', include('mlm.urls')),
    path('', include('mlm.urls')),
]
