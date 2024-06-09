from django.urls import path
from .views import RegisterView, UserView, LoginView, ReferredUsersView, RecentActivityList, ProfileView
from .views import UserDetailView, ReferralURLView, referred_users, update_user
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('api/referral-url/', ReferralURLView.as_view(), name='referral-url'),
    path('api/user/', UserView.as_view(), name='user'),
    path('login/', LoginView.as_view(), name='login'),
    path('referred-users/', ReferredUsersView.as_view(), name='referred_users'),
    path('api/recent-activity/', RecentActivityList.as_view(), name='recent_activity'),
    path('api/user-detail/', UserDetailView.as_view(), name='user_detail'),
    path('api/referred-users/', referred_users, name='referred_users'),
    path('api/user-detail/', UserDetailView.as_view(), name='user_detail'),
    path('api/recent-activity/', RecentActivityList.as_view(), name='recent_activity'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/update-user/', update_user, name='update_user'),
    path('', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]
