# 우리가 만든 user 모델
from .models import User
# django에서 제공하는 기본 password validation
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers # rest_framework의 serializers
from rest_framework.authtoken.models import Token # 토큰 모델
from rest_framework.validators import UniqueValidator # 중복 검사
from django.contrib.auth import authenticate
# authenticate: 사용자 인증 함수, 토큰을 발급받기 위해 사용

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())] # 중복 검사
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())] # 중복 검사
    )
    nickname = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())] # 중복 검사
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password]) # 비밀번호 유효성 검사
    password2 = serializers.CharField(write_only=True, required=True) # 비밀번호 확인

    class Meta:
        model = User
        fields = '__all__' # ['필드명'] 이렇게 하는 것은 이제 허용하지 않음
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': '비밀번호가 일치하지 않습니다.'})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username = validated_data['username'],
            email = validated_data['email'],
            nickname = validated_data['nickname'],
        )
        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user) # 토큰 생성
        return user
        

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    # write_only=True: password 필드는 읽기 전용으로 설정

    def validate(self, data):
        print(data)
        user = authenticate(**data)
        print(user)
        if user:
            token = Token.objects.get(user=user)
            return token
        raise serializers.ValidationError("유효하지 않은 로그인입니다.")
    
