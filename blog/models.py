from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = [
        ('reader', 'Lecteur'),
        ('author', 'Auteur'),
        ('moderator', 'Modérateur'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')

    def __str__(self):
        return f"{self.user.username} {self.role}"

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

class Article(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        null=True
    )
    edition = models.TextField(null=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta : 
        ordering = ['-cree_le']

    def __str__(self):
        return self.titre

class Commentaire(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='commentaires'
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commentaires'
    )
    contenu = models.TextField()
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta : 
        ordering = ['cree_le']

    def __str__(self):
        return f"Commentaire de {self.auteur} sur {self.article}"
