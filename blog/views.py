from rest_framework import viewsets, permissions
from .models import Article, Commentaire
from .serializers import ArticleSerializer, CommentaireSerializer
from .permissions import IsOwnerOrReadOnly, IsModeratorOrOwner

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-cree_le')
    serializer_class = ArticleSerializer
    filterset_fields = ['titre']
    search_fields = ['titre', 'contenu', 'edition', 'auteur']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,  IsModeratorOrOwner]

    def perform_create(self, serializer):
        serializer.save(auteur=self.request.user)

class CommentaireViewSet(viewsets.ModelViewSet):
    queryset = Commentaire.objects.select_related('article', 'auteur')
    serializer_class = CommentaireSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsModeratorOrOwner]

    def perform_create(self, serializer):
        serializer.save(auteur=self.request.user)
