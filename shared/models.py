from django.db import models
import uuid


class Basemodel(models.Model):
    id = models.UUIDField(unique=True,default=uuid.uuid4(), editable=False, primary_key=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

# Bu meta clas dagi abstarct =True degani meros olish uchun qilingan data bazaga saqlanmaydi
    class Meta:
        abstract = True


