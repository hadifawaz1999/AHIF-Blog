from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Like,Notification

@receiver(post_save,sender=Like)
def create_notification(sender,instance,created,**kwargs):
    if created:
        user = instance.user
        post = instance.post
        Notification.objects.create(user=user,post=post,like=instance)
