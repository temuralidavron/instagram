from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from shared.utility import check_email_or_phone, send_email, check_user_type
from .models import User,UserConfirmation, VIA_PHONE, VIA_EMAIL, NEW, CODE_VERIFIED, DONE, PHOTO_STEP
from rest_framework import exceptions
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)


    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)


    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status'
        )

        extra_kwargs = {
            'auth_type':{'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False}
        }
    def create(self, validated_data):
        user = super(SignUpSerializer,self).create(validated_data)
        print(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            print(code)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
            print(code)
            #send_phone_code(user.photo_number, code)
            user.save()
        return user


# Ushbu funksiya  birinchi validate ishga tushadi va u auth_validateni ham chaqiraadi

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data


    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input)
        if input_type == "email":
            data = {
                "email":user_input,
                "auth_type": VIA_EMAIL,
            }
        elif input_type == "phone":
            data = {
                "phone_number": user_input,
                "auth_type": VIA_PHONE,
            }
        else:
            data = {
                "success": False,
                "massage": "Must you send email or phone number"
            }
            raise ValidationError(data)
        print("data", data)
        return data


    def validate_email_phone_number(self, value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            data = {
                'success': False,
                'massage': "Bu email orqali ro'yxatdan o'tilgan bazada bor"

            }
            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                'success': False,
                'massage': "Bu phone orqali ro'yxatdan o'tilgan bazada bor",
            }
            raise ValidationError(data)
        return value


    def to_representation(self, instance):
        print("to rep", instance)
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())

        return data



class ChangeUserInformation(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get['password', None]
        confirm_password = data.get['confirm_password', None]
        if password != confirm_password:
            raise ValidationError(
                {
                    "success":False,
                    "message": "Kodlaringiz bir biriga to'g'ri emas"
                }
            )
        if password:
            validate_password(password)
            validate_password(confirm_password)
        return data

    def validate_username(self, username):
        if len(username)<5 and len(username)>35:
            raise ValidationError(
                {
                    "message": "Username 5ta belgidan kam bo'lmasiligi va 30ta belgidan ko'p bo'lmasligi kerak"
                }
            )
        if username.isdigit():
            raise ValidationError(
                {
                    "message": " Username raqamlardan iborat bo'lmasligi kerak "
                }
            )
        return username

    def validate_first_name(self, first_name):
        if len(first_name)<5 and  len(first_name)>35:
            raise ValidationError(
                {
                    "message": "Firstname 5ta belgidan kam bo'lmasiligi va 30ta belgidan ko'p bo'lmasligi kerak"
                }
            )
        if first_name.isdigit():
            raise ValidationError(
                {
                    "message": " Firstname raqamlardan iborat bo'lmasligi kerak "
                }
            )
        return first_name

    def validate_last_name(self, last_name):
        if len(last_name) < 5 and len(last_name) > 35:
            raise ValidationError(
                {
                    "message": "last_name 5ta belgidan kam bo'lmasiligi va 30ta belgidan ko'p bo'lmasligi kerak"
                }
            )
        if last_name.isdigit():
            raise ValidationError(
                {
                    "message": " last_name raqamlardan iborat bo'lmasligi kerak "
                }
            )
        return last_name


    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.password = validated_data.get('password', instance.password)
        instance.confirmed_password = validated_data.get('confirmed_password', instance.confirmed_password)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.ave()
        return instance


class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=(
        'jpg', 'jpeg', 'png', 'heic', 'heif'
    ))])


    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_STEP
            instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['user_input'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=True, read_only=True)


    def auth_validate(self, data):
        user_input = data.get('user_input')
        if check_user_type(user_input) == 'username':
            username = user_input

        elif check_user_type(user_input) == 'email':
            user = self.get(email__iexact=user_input)
            username = user.username

        elif check_user_type(user_input) == 'phone_number':
            user = self.get(phone_number=user_input)
            username = user.username
        else:
            data = {
                "success": False,
                "message": "Siz email, phone number yoki username jo'natishingiz kerak"
            }
            raise ValidationError(data)

        authenticated_kwargs = {
            self.username_field: username,
            'password': data['password']

        }
        current_user = User.objects.filter(username__iexact=username).first()
        if current_user is not None and current_user.auth_status in (NEW, CODE_VERIFIED):
            raise ValidationError(
                {
                    "success": False,
                    "message": "Siz ro'yxatdan to'liq o'tmagansiz"
                }
            )
        user = authenticate(**authenticated_kwargs)
        if user is not None:
            self.user = user
        else:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Sorry login or password you entred  is incorrect.Pleace check in try again"
                }
            )

    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not user.exists():
            raise ValidationError({
                "messsage": "Not active account found"
            })
        return users.first()




    def validate(self,data):
        self.auth_validate(date)
        if self.user.auth_status not in (DONE,PHOTO_STEP):
            raise PermissionDenied("Sizlogin qilaolmaysiz ruxsatingiz yo'q")
        data = self.user.token()
        data['auth_status'] = self.auth_status
        return data


class LoginRefreshSerializer(TokenObtainPairSerializer):


    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data('access'))
        user_id = access_token_instance['userd_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()






class ForgotPasswordSerializer(serializers.Serializer):
    eamil_or_phone = serializers.CharField(write_only=True,required=True)


    def validate(self, data):
        email_or_phone = self.data.get('email_or_phone', None)
        if email_or_phone is None:
            raise ValidationError(
                {
                    "success":False,
                    "message": "Email yoki raqam kkiritilishi shart"
                }
            )
        user = User.objects.filter(Q(email=email_or_phone) | Q(phone_number=email_or_phone))
        if not user.exists():
            raise NotFound(detail="User not found")
        data['user'] = user.first()
        return data


class RestePasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True,)
    password = serializers.CharField(max_length=8, required=True,write_only=True)
    confirm_password = serializers.CharField(max_length=8, required=True,write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'password',
            'confirm_password'
        )

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Password va tasdiqlash pasword teng emas",

                }
            )
        if password:
            validate_password(password)
        return data

    def update(self, instance, validated_data):
        password =validated_data.pop('password')
        instance.set_password(password)
        return super(RestePasswordSerializer,self).update(instance, validated_data)


