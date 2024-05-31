from rest_framework import serializers
from .models import User, Referral, Commission, RecentActivity, Activity, Commission

class UserSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'password', 'referral_code', 'referred_by', 'earnings', 'total_sales', 'profile_picture')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        referral_code = validated_data.pop('referral_code', None)
        referred_by = None
        if referral_code:
            referred_by = User.objects.filter(referral_code=referral_code).first()
        
        user = User.objects.create_user(**validated_data)
        if referred_by:
            user.referred_by = referred_by
            user.save()
            self.create_referral_tree(user, referred_by)
        
        return user

    def create_referral_tree(self, user, referred_by):
        if referred_by:
            level = 1
            parent = referred_by
            while parent and level <= 5:
                Referral.objects.create(referrer=parent, referred=user, level=level)
                commission_amount = self.calculate_commission(level)
                Commission.objects.create(user=parent, amount=commission_amount, level=level)
                parent = parent.referred_by
                level += 1

    def calculate_commission(self, level):
        commission_rates = {1: 0.30, 2: 0.20, 3: 0.15, 4: 0.10, 5: 0.10}
        return commission_rates.get(level, 0) * 40  # Example amount calculation

class RecentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecentActivity
        fields = ['activity', 'timestamp']

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['user', 'activity_type', 'description', 'timestamp']

class CommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = '__all__'