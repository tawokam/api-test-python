from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, CommentaireViewSet

router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='article')
router.register('commentaires', CommentaireViewSet, basename='commentaire')

urlpatterns = router.urls