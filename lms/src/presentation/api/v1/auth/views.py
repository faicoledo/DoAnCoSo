"""
Authentication API Views

Clean Architecture approach:
1. View receives request
2. View extracts data and creates DTO
3. View calls Use Case with DTO
4. Use Case returns result DTO
5. View converts result to response
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterInputSerializer,
    LoginInputSerializer,
    UserOutputSerializer,
    UpdateProfileInputSerializer,
)
from .....application.dtos.user import RegisterUserDTO, UpdateUserDTO
from .....application.use_cases.auth import (
    RegisterUserUseCase,
    GetCurrentUserUseCase,
    UpdateUserProfileUseCase,
    GetCurrentUserInput,
    UpdateUserInput,
)
from .....infrastructure.persistence.repositories import (
    DjangoUserRepository,
    DjangoEnrollmentRepository,
)
from .....domain.exceptions.user import (
    UserAlreadyExistsException,
    UserNotFoundException,
)


class RegisterView(APIView):
    """
    POST /api/v1/auth/register/
    Register a new user account
    """
    permission_classes = [AllowAny]
    parser_classes = [FormParser, MultiPartParser, JSONParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    serializer_class = RegisterInputSerializer
    
    def get_serializer(self, *args, **kwargs):
        """Return the serializer instance for browsable API form"""
        return self.serializer_class(*args, **kwargs)
    
    def post(self, request):
        # Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Create DTO
        dto = RegisterUserDTO(
            email=data['email'],
            full_name=data['full_name'],
            password=data['password'],
            password_confirm=data['password_confirm'],
        )
        
        # Execute use case
        user_repo = DjangoUserRepository()
        use_case = RegisterUserUseCase(user_repo)
        
        try:
            result = use_case.execute(dto)
        except UserAlreadyExistsException as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Return response
        output_serializer = UserOutputSerializer(result)
        return Response(
            {
                'message': 'Đăng ký thành công.',
                'user': output_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    POST /api/v1/auth/login/
    Login with email OR username + password
    
    Accepts:
    - username: có thể là email hoặc username
    - password: mật khẩu
    """
    permission_classes = [AllowAny]
    parser_classes = [FormParser, MultiPartParser, JSONParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    serializer_class = LoginInputSerializer
    
    def get_serializer(self, *args, **kwargs):
        """Return the serializer instance for browsable API form"""
        return self.serializer_class(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        # Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username_or_email = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        from django.contrib.auth.models import User
        from django.contrib.auth import authenticate
        
        # Try to find user by email or username
        user = None
        
        # Check if input looks like an email (contains @)
        if '@' in username_or_email:
            # Try to find by email
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                pass
        
        # If not found by email, try by username
        if user is None:
            try:
                user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                pass
        
        # If still not found, return error
        if user is None:
            return Response(
                {'detail': 'Tài khoản hoặc mật khẩu không đúng.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Authenticate with password
        authenticated_user = authenticate(username=user.username, password=password)
        if not authenticated_user:
            return Response(
                {'detail': 'Tài khoản hoặc mật khẩu không đúng.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is active
        if not authenticated_user.is_active:
            return Response(
                {'detail': 'Tài khoản đã bị vô hiệu hóa.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate tokens
        refresh = RefreshToken.for_user(authenticated_user)
        
        # Get user data
        user_repo = DjangoUserRepository()
        user_entity = user_repo.find_by_id(authenticated_user.id)
        
        output_serializer = UserOutputSerializer({
            'id': user_entity.id,
            'email': user_entity.email,
            'full_name': user_entity.full_name,
            'role': user_entity.role.value if user_entity.role else 'STUDENT',
            'role_display': user_entity.role.display_name if user_entity.role else 'Học viên',
        })
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': output_serializer.data,
        })


class CurrentUserView(APIView):
    """
    GET /api/v1/auth/me/
    Get current user profile
    
    PATCH /api/v1/auth/me/
    Update current user profile
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser, JSONParser]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    serializer_class = UpdateProfileInputSerializer
    
    def get_serializer(self, *args, **kwargs):
        """Return the serializer instance for browsable API form"""
        return self.serializer_class(*args, **kwargs)
    
    def get(self, request):
        # Create input DTO
        input_dto = GetCurrentUserInput(user_id=request.user.id)
        
        # Execute use case
        user_repo = DjangoUserRepository()
        enrollment_repo = DjangoEnrollmentRepository()
        use_case = GetCurrentUserUseCase(user_repo, enrollment_repo)
        
        try:
            result = use_case.execute(input_dto)
        except UserNotFoundException as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        output_serializer = UserOutputSerializer(result.__dict__)
        return Response(output_serializer.data)
    
    def patch(self, request):
        # Validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Create DTOs
        update_dto = UpdateUserDTO(
            email=data.get('email'),
            full_name=data.get('full_name'),
            phone=data.get('phone'),
            bio=data.get('bio'),
            avatar=data.get('avatar'),
            password=data.get('password'),
            password_confirm=data.get('password_confirm'),
        )
        input_dto = UpdateUserInput(user_id=request.user.id, data=update_dto)
        
        # Execute use case
        user_repo = DjangoUserRepository()
        use_case = UpdateUserProfileUseCase(user_repo)
        
        try:
            result = use_case.execute(input_dto)
        except UserNotFoundException as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        output_serializer = UserOutputSerializer(result.__dict__)
        return Response({
            'message': 'Cập nhật thông tin thành công.',
            'user': output_serializer.data,
        })
