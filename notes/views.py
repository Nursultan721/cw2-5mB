from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken

from .models import Note
from .pagination import NotePagination
from .permissions import IsOwnerOrReadOnly
from .serializers import NoteSerializer, RegisterSerializer, UserSerializer


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(auth=[], tags=['auth'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginView(ObtainAuthToken):
    @extend_schema(auth=[], tags=['auth'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.select_related('owner').all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = NotePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {'title': ['exact', 'icontains']}
    search_fields = ['title', 'content']
    ordering_fields = ['id', 'title']
    ordering = ['id']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
