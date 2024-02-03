from rest_framework import routers

from book_service.views import BookViewSet


router = routers.DefaultRouter()
router.register("", BookViewSet)


urlpatterns = router.urls


app_name = "book_service"
