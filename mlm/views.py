from rest_framework import generics, permissions, status
from django.http import JsonResponse
from django.views.generic.edit import UpdateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from .models import User, Referral, Commission, Activity
from .serializers import UserSerializer, ActivitySerializer, CommissionSerializer
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from decimal import Decimal

User = get_user_model()

# User detail view using APIView
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

# Register view with referral handling
class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        referral_code = request.data.get('referral_code')
        referred_by = None
        if referral_code:
            try:
                referred_by = User.objects.get(referral_code=referral_code)
            except User.DoesNotExist:
                return Response({"error": "Invalid referral code"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(referred_by=referred_by)
            self.create_referral_tree(user, referred_by)

            # Generate JWT token
            token_serializer = TokenObtainPairSerializer(data={
                'username': request.data['username'],
                'password': request.data['password']
            })
            token_serializer.is_valid(raise_exception=True)
            tokens = token_serializer.validated_data

            return Response({'access': tokens['access']}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_referral_tree(self, user, referred_by):
        if referred_by:
            level = 1
            parent = referred_by
            while parent and level <= 5:
                Referral.objects.create(referrer=parent, referred=user, level=level)
                # Calculate commission for the parent
                commission_amount = self.calculate_commission(level)
                Commission.objects.create(user=parent, amount=commission_amount, level=level)
                parent = parent.referred_by
                level += 1

    def calculate_commission(self, level):
        commission_rates = {1: 0.30, 2: 0.20, 3: 0.15, 4: 0.10, 5: 0.10}
        return commission_rates.get(level, 0) * 100  # Example amount calculation

# User view using RetrieveAPIView
class UserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# Referred users view
class ReferredUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        referrals = user.referrals_made.all()  # User's direct referrals
        referred_users = [
            {
                'username': referral.username,
                'referred_users': [
                    sub_referral.username
                    for sub_referral in referral.referrals_made.all()
                ]
            }
            for referral in referrals
        ]
        return Response(referred_users)

# Login view using APIView
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

# Recent activity list view
class RecentActivityList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activities = Activity.objects.filter(user=request.user).order_by('-timestamp')[:10]
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)

# Activity list view using ListAPIView
class ActivityListView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Activity.objects.filter(user=user).order_by('-timestamp')

# Recent activities using function-based view
@api_view(['GET'])
def recent_activities(request):
    activities = Activity.objects.filter(user=request.user).order_by('-timestamp')[:10]
    serializer = ActivitySerializer(activities, many=True)
    return Response(serializer.data)

# Profile view using APIView
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            # Add other user details as needed
        })


class UserDetailUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ReferralURLView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        referral_url = f"{settings.FRONTEND_URL}/register?referral={user.referral_code}"
        return Response({"referral_url": referral_url})

@api_view(['GET'])
def get_referral_url(request):
    user = request.user
    referral_url = f"https://dpsmlm.co.za/register?referral={user.username}"
    return Response({"referral_url": referral_url})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def referred_users(request):
    user = request.user
    referrals = user.referrals_made.all()
    referred_users = [
        {
            'username': referral.username,
            'referred_users': [
                sub_referral.username
                for sub_referral in referral.referrals_made.all()
            ]
        }
        for referral in referrals
    ]
    return Response(referred_users)

class CommissionListView(generics.ListAPIView):
    serializer_class = CommissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Commission.objects.filter(user=self.request.user)


class SaleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        amount = Decimal(request.data.get('amount', '0.00'))

        # Update user sales
        user.total_sales += amount
        user.save()

        # Calculate commissions
        self.calculate_commissions(user, amount)

        return Response({'message': 'Sale recorded and commissions calculated'})
    
def calculate_commissions(self, user, amount):
        # Direct sales commission
        user.earnings += amount * Decimal('0.20')
        user.save()

        # Recruitment commission and residual income
        current_level_user = user.referred_by
        level = 1

        while current_level_user and level <= 5:
            commission_rate = {1: 0.10, 2: 0.15, 3: 0.20, 4: 0.25, 5: 0.30}.get(level, 0)
            current_level_user.earnings += amount * commission_rate
            current_level_user.save()

            current_level_user = current_level_user.referred_by
            level += 1    