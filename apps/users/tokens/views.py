from apps.users.tokens.serializers import (TokenObtainPairSerializer,
                                           TokenObtainSlidingSerializer,
                                           TokenRefreshSerializer,
                                           TokenRefreshSlidingSerializer,
                                           TokenVerifySerializer)
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenViewBase


class TokenObtainPairView(TokenViewBase):
    permission_classes = [AllowAny]
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = TokenObtainPairSerializer


class TokenRefreshView(TokenViewBase):
    permission_classes = [AllowAny]
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """
    serializer_class = TokenRefreshSerializer


class TokenObtainSlidingView(TokenViewBase):
    permission_classes = [AllowAny]
    """
    Takes a set of user credentials and returns a sliding JSON web token to
    prove the authentication of those credentials.
    """
    serializer_class = TokenObtainSlidingSerializer


class TokenRefreshSlidingView(TokenViewBase):
    permission_classes = [AllowAny]
    """
    Takes a sliding JSON web token and returns a new, refreshed version if the
    token's refresh period has not expired.
    """
    serializer_class = TokenRefreshSlidingSerializer


class LoginCheckView(APIView):
    def post(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


class TokenVerifyView(TokenViewBase):
    """
    Takes a token and indicates if it is valid.  This view provides no
    information about a token's fitness for a particular use.
    """
    serializer_class = TokenVerifySerializer
