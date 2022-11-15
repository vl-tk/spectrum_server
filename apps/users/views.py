import json

from apps.users.models import User
from apps.users.serializers import (ChangePasswordSerializer,
                                    CheckResetCodeSerializer,
                                    ConfirmEmailSerializer,
                                    ConfirmNewEmailSerializer,
                                    RequestChangeEmailSerializer,
                                    RequestResetPasswordSerializer,
                                    ResendConfirmEmailSerializer,
                                    ResetPasswordSerializer,
                                    UserRegisterSerializer, UserSerializer)
from apps.users.tokens.serializers import TokenObtainPairSerializer
from django.http import Http404
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse


class OAuthRegistrationView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]

    class OAuthLoginRequestSerializer(serializers.Serializer):
        backend = serializers.ChoiceField(
            required=True,
            write_only=True,
            choices=('google-oauth2', 'facebook')
        )
        access_token = serializers.CharField(
            required=True,
            write_only=True,
            allow_blank=True,
            allow_null=True,
            help_text='access_token from service like google, twitter etc.'
        )
        register = serializers.BooleanField(
            write_only=True,
            default=False,
            help_text="Enable new user registration"
        )
    class OAuthLoginResponseSerializer(serializers.Serializer):
        refresh = serializers.CharField(required=True)
        access = serializers.CharField(required=True)

    # @swagger_auto_schema(
    #     query_serializer=OAuthLoginRequestSerializer(),
    #     responses={
    #         status.HTTP_200_OK: OAuthLoginResponseSerializer(),
    #         status.HTTP_403_FORBIDDEN: '',
    #     }
    # )
    def get(self, request, *args, **kwargs):
        redirect_uri = 'social:complete'
        uri = redirect_uri
        serializer = OAuthRegistrationView.OAuthLoginRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        backend = serializer.validated_data.get('backend')
        token = serializer.validated_data.get('access_token')

        register = serializer.validated_data.get('register')
        if uri and not uri.startswith('/'):
            uri = reverse(redirect_uri, args=(backend,))
        request.social_strategy = load_strategy(request)
        # backward compatibility in attribute name, only if not already
        # defined
        if not hasattr(request, 'strategy'):
            request.strategy = request.social_strategy

        try:
            request.backend = load_backend(request.social_strategy, backend, uri)
        except MissingBackend:
            raise Http404('Backend not found')
        # This view expects an access_token GET parameter, if it's needed,
        # request.backend and request.strategy will be loaded with the current
        # backend and strategy.
        user = request.backend.do_auth(token, response=None, register=register)
        if user:
            refresh = TokenObtainPairSerializer.get_token(user)
            data = {'refresh': str(refresh), 'access': str(refresh.access_token)}
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class UserCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer


class UserView(generics.RetrieveAPIView):
    """
    Public profile view - only Chefs and Customers
    """

    permission_classes = [AllowAny]
    queryset = User.objects.all().get_active().get_not_banned()
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            obj = self.queryset.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404
        return obj


class UserMeRetrieveUpdateView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.data.get('data'):
            data = dict(**json.loads(request.data.get('data')))
            if 'avatar' in request.data:
                data.update(dict(avatar=request.data.get('avatar')))
        else:
            data = request.data

        serializer = self.get_serializer(instance, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ConfirmEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConfirmEmailSerializer

    # @swagger_auto_schema(responses={200: ''})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.confirm_email()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class RequestChangeEmailView(generics.GenericAPIView):
    serializer_class = RequestChangeEmailSerializer

    # @swagger_auto_schema(responses={200: ''})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_confirm_new_email(request.data)
        data = dict(code=self.request.user.activation_email_code)
        return Response(data=data, status=status.HTTP_200_OK)


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer

    # @swagger_auto_schema(responses={200: ''})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.set_password()
        return Response(status=status.HTTP_200_OK)


class ConfirmNewEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConfirmNewEmailSerializer

    # @swagger_auto_schema(responses={200: ''})
    def post(self, request):
        serializer = self.get_serializer(data={'code': self.kwargs['code']})
        serializer.is_valid(raise_exception=True)
        serializer.confirm_new_email()
        return Response({}, status=status.HTTP_200_OK)


class RequestResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RequestResetPasswordSerializer

    # @swagger_auto_schema(responses={200: ''})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.send_make_new_password()
        return Response(data=None, status=status.HTTP_200_OK)


class CheckResetCodeView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CheckResetCodeSerializer

    # @swagger_auto_schema(responses={200: ''})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    # @swagger_auto_schema(responses={200: ''})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.reset_password()
        return Response(status=status.HTTP_200_OK)


class ResendConfirmEmailView(generics.GenericAPIView):
    serializer_class = ResendConfirmEmailSerializer

    # @swagger_auto_schema(responses={200: ""})
    def post(self, request):
        serializer = self.get_serializer(request.user)
        serializer.send_confirm_email()
        return Response(data=None, status=status.HTTP_200_OK)
