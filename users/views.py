from datetime import datetime

from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utility import send_email, check_email_or_phone
from .models import User, NEW, CODE_VERIFIED, VIA_EMAIL, VIA_PHONE
from .serializer import SignUpSerializer, ChangeUserInformation, ChangeUserPhotoSerializer, LoginSerializer, \
    LoginRefreshSerializer, LogoutSerializer, ForgotPasswordSerializer, RestePasswordSerializer


class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny,]


class VerifyAPIView(APIView):
    permission_classes = [IsAuthenticated,]


    def post(self,request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify(user, code)
        return Response(
            data={
                "success":True,
                "auth_status":user.auth_status,
                "access":user.token()['access'],
                "refresh":user.token()["refresh_token"]


            }
        )


    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        if not verifies.exists():
            data = {
                "messsage": "Tasdiqlash kodingiz xato yoki eskirgan "
            }
            raise ValidationError(data)
        else:
            verifies.update(is_conirmed=True)
        if user.auth_status not in NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True


class GetNewVerification(APIView):


    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verifiction(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
        else:
            data = {
                "message": "Email yoki phone number noto'g'ri"
            }
            raise ValidationError(data)



    @staticmethod
    def check_verifiction(user):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if verifies.exists():
            data = {
                "success": False,
                "message": "Kodingiz yuborilgan o'sha kodni kiriting"

            }
            raise ValidationError(data)

        return Response(
            {
                "succeess": False,
                "message": "Tasdiqlash kodingiz qaytadan jo'natildi"
            }
        )


class ChangeUserInformationVeiw(UpdateAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = ChangeUserInformation
    http_method_names = ['patch','put']


    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationVeiw, self).update(request, *args, **kwargs)
        data = {
            "success": True,
            "messege": "O'zgartilidi",
            "auth_status": self.request.user.auth_status
        }
        return Response(data, status=200)

    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationVeiw, self).partial_update(request, *args, **kwargs)
        data = {
            "success": True,
            "messege": "O'zgartilidi",
            "auth_status": self.request.user.auth_status
        }
        return Response(data, status=200)

class ChangeUserPhotoView(APIView):
    permission_classes = [IsAuthenticated, ]


    def put(self,request, *args, **kwargs):
        serializer = ChangeUserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.update(user, serializer.validated_data)
            return Response(
                {
                    "message": "Rasm almashtirildi"
                },
            status=200)
        return Response(serializer.errors, status=400)


class LoginVew(TokenObtainPairView):
    serializer_class = LoginSerializer



class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer


class LogOutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated, ]


    def post(self,request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                "success": True,
                "message": "You are logout out"

            }
            return Response(data, status=205)
        except TokenError:
            return Response(status=400)


class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny, ]


    def post(self,request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid()
        email_or_phone = serializer.validated_data.get('email_or_phone')
        user = serializer.validated_data.get('user')
        if check_email_or_phone(email_or_phone) =='phone':
            code = user.create_verify_code(VIA_PHONE)
            send_email(email_or_phone, code)

        elif check_email_or_phone(email_or_phone) == 'email':
            code = user.create_verify_code(VIA_EMAIL)
            send_email(email_or_phone, code)

        return Response(
            {
                "succees": True,
                "message": "Tasdiqlash kodi yuborildi",
                "access": user.token()['refresh'],
                "refresh": user.token()['refresh_token'],
                "user": user.auth_status,
            }, status=200

        )


class ResetPasswordView(UpdateAPIView):
    serializer_class = RestePasswordSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user


    def update(self, request, *args, **kwargs):
        response = super(ResetPasswordView, self).update(request, *args, **kwargs)
        try:
            user = User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist as e:
            raise NotFound(detail="User not found")

        return Response(
            {
                "success": False,
                "message": "Parolingiz muvofaqiyatli o'zgartirildi",
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token'],

            }
        )









