from rest_framework import serializers
from .models import Article, Commentaire

class CommentaireSerializer(serializers.ModelSerializer):
    auteur = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Commentaire
        fields = '__all__'
        read_only_fields = ('cree_le', 'auteur')


class ArticleSerializer(serializers.ModelSerializer):
    queryset = (
        Article.objects
        .select_related('auteur')
        .prefetch_related('commentaires__auteur')
        .order_by('-cree_le')
    )
    auteur = serializers.StringRelatedField(read_only=True)
    commentaires = CommentaireSerializer(many=True, read_only=True)
    nb_commentaires = serializers.IntegerField(
        source='commentaires.count', read_only=True
    )
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('cree_le', 'auteur')