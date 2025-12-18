"""
Custom Admin Site - Chỉ cho phép user có role ADMIN truy cập
User ADMIN sẽ có toàn quyền truy cập tất cả chức năng
"""
from django.contrib import admin
from django.contrib.admin import AdminSite


class LMSAdminSite(AdminSite):
    site_header = 'LMS Administration'
    site_title = 'LMS Admin'
    index_title = 'Quản trị hệ thống LMS'
    
    def has_permission(self, request):
        """
        Chỉ cho phép user có role ADMIN truy cập admin site.
        User ADMIN được coi như có toàn quyền (tương đương superuser trong admin).
        """
        if not request.user.is_active:
            return False
        
        # Superuser luôn được truy cập
        if request.user.is_superuser:
            return True
        
        # Kiểm tra role ADMIN trong profile - có toàn quyền
        try:
            if hasattr(request.user, 'profile') and request.user.profile:
                return request.user.profile.role == 'ADMIN'
        except Exception:
            pass
        
        return False


# Tạo instance của custom admin site
lms_admin_site = LMSAdminSite(name='lms_admin')

# Monkey patch để user ADMIN có toàn quyền trong admin
_original_has_perm = None

def setup_admin_permissions():
    """
    Cấu hình để user có role ADMIN có toàn quyền trong Django Admin
    """
    from django.contrib.auth.models import User
    
    global _original_has_perm
    if _original_has_perm is None:
        _original_has_perm = User.has_perm
    
    def custom_has_perm(self, perm, obj=None):
        # Superuser có toàn quyền
        if self.is_superuser:
            return True
        
        # User có role ADMIN cũng có toàn quyền trong admin
        try:
            if hasattr(self, 'profile') and self.profile and self.profile.role == 'ADMIN':
                return True
        except Exception:
            pass
        
        # Các user khác kiểm tra quyền bình thường
        return _original_has_perm(self, perm, obj)
    
    User.has_perm = custom_has_perm

# Gọi setup khi module được import
setup_admin_permissions()

