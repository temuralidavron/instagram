import random
import uuid
from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import Basemodel

ORDINARY_USER, MANAGER, ADMIN = ("ordinary_user", "manager", "admin")
VIA_PHONE, VIA_EMAIL = ('via_phone', 'via_email')
NEW, CODE_VERIFIED, DONE, PHOTO_STEP = ("new", "code_verified", "done", "photo_step")


class User(AbstractUser, Basemodel):
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),  #Bu statusni '' qa olmaganimizni sababi unga modeldan tashqarida ham foydalanish mumkin
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )
    AUTH_TYPE_CHOICES = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL)
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP)
    )
    user_roles = models.CharField(max_length=31, choices=USER_ROLES, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=31, choices=AUTH_TYPE_CHOICES)  #userning saytga qanday kirishini belgilaydi email yoki photo
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)  # Bu esa signupning bosqichlarini belgilash uchun
    email = models.EmailField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True, unique=True)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png', 'heic', 'heif'])])

    def __str__(self):
        return self.username


# Ushbu funksiyanivazifasi username.full_name ni chaqirganda ism familiyani to'liq chiqaradi
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# 4 ta raqamli kodni olish uchun yaratilgan funksiya
    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(0, 100) % 10) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id=self.id,
            verify_type=verify_type,
            code=code
        )
        return code


# User phone yoki email orqali murojat etganda unga user fieldlari to'liq ochiladi
# uni vaqtinchalik toldirish uchun ushbu funfsiya yaratilyapti

    def check_username(self):
        if not self.username:
            temp_username = f"instagram-{uuid.uuid4().__str__().split('-')[-1]}"
            while User.objects.filter(username=temp_username):
                temp_username = f"{temp_username} {random.randint(0,9)}"
            self.username = temp_username


    def check_email(self):
        if self.email:
            normalize_email = self.email.lower()
            self.email = normalize_email

    def check_pass(self):
        if not self.password:
            temp_password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
            self.password = temp_password
# PAraolni shriftlangan holatda saqlash uchun ishlatildi
    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)


    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh_token": str(refresh)
        }

    def clean(self):
        self.check_email()
        self.check_username()
        self.check_pass()
        self.hashing_password()

# Malumotlar bazasiga saqlash uchun
    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)



PHONE_EXPIRE = 2
EMAIL_EXPIRE = 5


class UserConfirmation(Basemodel):
    TYPE_CHOICE = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL)
    )
    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=31, choices=TYPE_CHOICE)
    user = models.ForeignKey('users.User', models.CASCADE, related_name='verif_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())
# UShbu funksiya vaqtni belgilab ushbu vaqt ichida kodni yozishni talab qiladi va super metodi malumotlar bazasiga saqlashni bildiradi
    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:
            self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
        else:
            self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation, self).save(*args, **kwargs)

