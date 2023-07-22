from django.urls import path
from .views import CreateUserView, VerifyAPIView, GetNewVerification, ChangeUserInformationVeiw, ChangeUserPhotoView, \
    LoginVew, LoginRefreshView, LogOutView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('login/', LoginVew.as_view()),
    path('login-refresh/', LoginRefreshView.as_view()),
    path('login-out/', LogOutView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
    path('signup/', CreateUserView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('new-verify/', GetNewVerification.as_view()),
    path('change-user/', ChangeUserInformationVeiw.as_view()),
    path('change-user-photo/', ChangeUserPhotoView.as_view()),
]