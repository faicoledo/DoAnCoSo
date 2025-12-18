"""
Authentication Serializers

These are DRF serializers for input validation and output formatting.
They are presentation layer concerns and should not contain business logic.
"""
from rest_framework import serializers


class RegisterInputSerializer(serializers.Serializer):
    """Input serializer for user registration"""
    email = serializers.EmailField(
        required=True,
        label="Email",
        help_text="Email sẽ được dùng để đăng nhập",
        style={'placeholder': 'example@email.com'}
    )
    full_name = serializers.CharField(
        max_length=255,
        required=True,
        label="Họ và tên",
        style={'placeholder': 'Nguyễn Văn A'}
    )
    password = serializers.CharField(
        write_only=True, 
        required=True,
        min_length=8,
        label="Mật khẩu",
        help_text="Tối thiểu 8 ký tự",
        style={'input_type': 'password', 'placeholder': 'Nhập mật khẩu'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        label="Xác nhận mật khẩu",
        style={'input_type': 'password', 'placeholder': 'Nhập lại mật khẩu'}
    )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Mật khẩu xác nhận không khớp.'
            })
        return attrs


class LoginInputSerializer(serializers.Serializer):
    """
    Input serializer for login
    Accepts either email or username in the 'username' field
    """
    username = serializers.CharField(
        required=True,
        label="Email / Username",
        help_text="Nhập email hoặc username của bạn",
        style={
            'placeholder': 'example@email.com hoặc username',
            'autofocus': True
        }
    )
    password = serializers.CharField(
        required=True,
        label="Mật khẩu",
        style={
            'input_type': 'password',
            'placeholder': 'Nhập mật khẩu'
        }
    )


class UpdateProfileInputSerializer(serializers.Serializer):
    """Input serializer for updating profile"""
    email = serializers.EmailField(
        required=False,
        label="Email",
        help_text="Email dùng để đăng nhập",
        style={'placeholder': 'example@email.com'}
    )
    full_name = serializers.CharField(
        max_length=255,
        required=False,
        label="Họ và tên",
        style={'placeholder': 'Nguyễn Văn A'}
    )
    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        label="Số điện thoại",
        style={'placeholder': '0123456789'}
    )
    bio = serializers.CharField(
        required=False,
        allow_blank=True,
        label="Giới thiệu",
        style={'placeholder': 'Mô tả ngắn về bạn...'}
    )
    avatar = serializers.ImageField(
        required=False,
        allow_null=True,
        label="Ảnh đại diện",
        help_text="Chọn ảnh đại diện (JPG, PNG)"
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        label="Mật khẩu mới",
        help_text="Để trống nếu không đổi mật khẩu",
        style={'input_type': 'password', 'placeholder': 'Nhập mật khẩu mới'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=False,
        label="Xác nhận mật khẩu",
        style={'input_type': 'password', 'placeholder': 'Nhập lại mật khẩu mới'}
    )
    
    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password or password_confirm:
            if not password or not password_confirm:
                raise serializers.ValidationError(
                    'Cần nhập cả mật khẩu mới và xác nhận mật khẩu.'
                )
            if password != password_confirm:
                raise serializers.ValidationError({
                    'password_confirm': 'Mật khẩu xác nhận không khớp.'
                })
        
        return attrs


class EnrollmentOutputSerializer(serializers.Serializer):
    """Output serializer for enrollment data"""
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    subject_title = serializers.CharField()
    role_in_course = serializers.CharField()
    role_display = serializers.CharField()
    status = serializers.CharField()
    joined_at = serializers.DateTimeField()


class UserOutputSerializer(serializers.Serializer):
    """Output serializer for user data"""
    id = serializers.IntegerField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    role = serializers.CharField()
    role_display = serializers.CharField()
    avatar = serializers.CharField(allow_null=True, required=False)
    phone = serializers.CharField(allow_blank=True, required=False)
    bio = serializers.CharField(allow_blank=True, required=False)
    enrollments = EnrollmentOutputSerializer(many=True, required=False)

