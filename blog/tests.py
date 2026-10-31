from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Article, Commentaire

User = get_user_model()

class ArticleAPITests(APITestCase):
    """Tests CRUD + permission sur /api/articles/"""

    def setUp(self):
        #Deux utilisateurs : un auteur, un intrus
        self.user = User.objects.create_user(username="alain", password="root")
        self.other = User.objects.create_user(username="aicha", password="root")

        self.article = Article.objects.create(
            titre='Article initial',
            contenu='Contenu initial',
            auteur=self.user,
        )
        self.list_url = reverse('article-list')
        self.detail_url = reverse('article-detail', args=[self.article.pk])

    # ---------- Lecture publique ------------
    def test_list_is_public(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1) #pagination

    def test_list_detail_is_public(self):
        res = self.client.get(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['titre'], 'Article initial')

    # ---------- Création protégée ------------
    def test_create_requires_auth(self):
        res = self.client.post(self.list_url, {'titre':'x', 'contenu':'y'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_sets_auteur_automatically(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self.list_url, {'titre':'nouveau', 'contenu': 'ok'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['auteur'], 'alain')
        self.assertEqual(Article.objects.count(), 2)

    #--------- Permission objet -------------
    def test_update_forbiden_for_non_owner(self):
        self.client.force_authenticate(user=self.other)
        res = self.client.patch(self.detail_url, {'titre':'piraté'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_allowes_for_owner(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.patch(self.detail_url, {'titre':'modifié'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.article.refresh_from_db()
        self.assertEqual(self.article.titre, 'modifié')

    def test_delete_forbidden_for_non_owner(self):
        self.client.force_authenticate(user=self.other)
        res = self.client.delete(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class CommentaireAPITests(APITestCase):
    """Tests relation article, commentaire + auth """

    def setUp(self):
        self.user = User.objects.create_user(username='alain', password='root')
        self.article = Article.objects.create(titre='A', contenu='B', auteur=self.user,)
        self.url = reverse('commentaire-list')

    def test_create_commentaire_require_auth(self):
        res = self.client.post(self.url, {'article': self.article.pk, 'contenu':'x'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        
    def test_create_commentaire_sets_auteur_and_article(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self.url, {
            'article': self.article.pk,
            'contenu': 'premier commentaire',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['auteur'], 'alain')
        self.assertEqual(res.data['article'], self.article.pk)
        self.assertEqual(self.article.commentaires.count(), 1)

    def test_article_detail_includes_commentaires_and_count(self):
        Commentaire.objects.create(article=self.article, auteur=self.user, contenu='c1')
        Commentaire.objects.create(article=self.article, auteur=self.user, contenu='c2')
        res = self.client.get(reverse('article-detail', args=[self.article.pk]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['nb_commentaires'], 2)
        self.assertEqual(len(res.data['commentaires']), 2)

class PermissionAdvanceTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='alain', password='root')
        self.other = User.objects.create_user(username='aicha', password='root')
        self.mado = User.objects.create_user(username='mado', password='root', is_staff=True)
        self.article = Article.objects.create(titre='T', contenu='C', auteur=self.author)

        self.detail = reverse('article-detail', args=[self.article.pk])

    def test_other_cannot_update(self):
        self.client.force_authenticate(user=self.other)
        res = self.client.patch(self.detail, {'titre':'x'})
        self.assertEqual(res.status_code, 403)

    def test_moderator_can_update(self):
        self.client.force_authenticate(user=self.mado)
        res = self.client.patch(self.detail, {'titre':'modéré'})
        self.assertEqual(res.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.titre, 'modéré')

    def test_anonymous_read_only(self):
        res = self.client.get(self.detail)
        self.assertEqual(res.status_code, 200)
        res = self.client.post(reverse('article-list'), {'titre':'x', 'contenu':'y'})
        self.assertEqual(res.status_code, 401)


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alain', password='root')

    def test_full_auth_flow(self):
        #login
        res = self.client.post(reverse('token_obtain_pair'), {
            'username': 'alain', 'password':'root'
        })
        self.assertEqual(res.status_code, 200)
        refresh = res.data['refresh']
        access = res.data['access']

        #Accès
        self.client.credentials(HTTP_AUTORIZATION='Bearer {access}')
        res = self.client.get(reverse('article-list'))
        self.assertEqual(res.status_code, 200)

        #blacklist du refresh
        self.client.credentials()
        res = self.client.post(reverse('token_blacklist'), {'refresh': refresh})
        self.assertEqual(res.status_code, 200)

        #Refresh avec l'ancien refresh : doit echouer
        res = self.client.post(reverse('token_refresh'), {
            'refresh': refresh
        })
        self.assertEqual(res.status_code, 401)