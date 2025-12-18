"""
Django Admin Configuration for LMS

Registers all models with the Django admin site.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from config.admin import lms_admin_site

from .models.user import UserProfileModel
from .models.course import SubjectModel, CourseModel, ModuleModel, LessonModel
from .models.enrollment import EnrollmentModel
from .models.content import ResourceModel
from .models.assessment import AssignmentModel, QuestionModel, AttemptModel, AttemptDetailModel
from .models.activity import UserActivityLogModel
from .models.communication import NotificationModel, CommentModel

# Sử dụng custom admin site cho tất cả các decorator @admin.register
admin.site = lms_admin_site


# ==================== USER ADMIN ====================

class UserProfileInline(admin.StackedInline):
    """Inline UserProfile in User admin"""
    model = UserProfileModel
    can_delete = False
    verbose_name = 'Hồ sơ'
    verbose_name_plural = 'Hồ sơ người dùng'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    """Extended User admin with profile"""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'get_full_name', 'get_role', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'profile__role', 'date_joined']
    search_fields = ['username', 'email', 'profile__full_name']
    
    def get_full_name(self, obj):
        try:
            return obj.profile.full_name
        except:
            return '-'
    get_full_name.short_description = 'Họ tên'
    
    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except:
            return '-'
    get_role.short_description = 'Vai trò'


# Register User with custom admin
lms_admin_site.register(User, CustomUserAdmin)


@admin.register(UserProfileModel, site=lms_admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'full_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']


# ==================== COURSE ADMIN ====================

@admin.register(SubjectModel, site=lms_admin_site)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'course_count', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = 'Số khóa học'


class ModuleInline(admin.TabularInline):
    """Inline Module in Course admin"""
    model = ModuleModel
    extra = 1
    ordering = ['order']


@admin.register(CourseModel, site=lms_admin_site)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'get_status', 'start_date', 'end_date', 'get_duration', 'student_count', 'teacher_count']
    list_filter = ['subject', 'start_date', 'end_date']
    search_fields = ['title', 'description', 'subject__title']
    readonly_fields = ['created_at', 'updated_at', 'get_status_display', 'get_time_info']
    inlines = [ModuleInline]
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('subject', 'title', 'description')
        }),
        ('Thời gian khóa học', {
            'fields': ('start_date', 'end_date'),
            'description': '⚠️ Trạng thái khóa học được tính TỰ ĐỘNG dựa trên ngày bắt đầu và kết thúc'
        }),
        ('Trạng thái (Tự động)', {
            'fields': ('get_status_display', 'get_time_info'),
            'classes': ('collapse',)
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status(self, obj):
        status = obj.computed_status
        colors = {
            'UPCOMING': '#17a2b8',    # Blue
            'ONGOING': '#28a745',     # Green
            'COMPLETED': '#6c757d',   # Gray
        }
        labels = {
            'UPCOMING': '🔵 Sắp diễn ra',
            'ONGOING': '🟢 Đang diễn ra',
            'COMPLETED': '⚫ Đã hoàn thành',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(status, '#000'),
            labels.get(status, status)
        )
    get_status.short_description = 'Trạng thái'
    get_status.admin_order_field = 'start_date'
    
    def get_status_display(self, obj):
        return self.get_status(obj)
    get_status_display.short_description = 'Trạng thái hiện tại'
    
    def get_time_info(self, obj):
        if not obj.start_date or not obj.end_date:
            return "⚠️ Chưa thiết lập thời gian"
        if obj.is_upcoming:
            return f"📅 Còn {obj.days_until_start} ngày nữa bắt đầu"
        elif obj.is_ongoing:
            return f"⏳ Còn {obj.days_until_end} ngày nữa kết thúc"
        else:
            return f"✅ Đã kết thúc {-obj.days_until_end} ngày trước"
    get_time_info.short_description = 'Thông tin thời gian'
    
    def get_duration(self, obj):
        if obj.duration_days is None:
            return "—"
        return f"{obj.duration_days} ngày"
    get_duration.short_description = 'Thời lượng'
    
    def student_count(self, obj):
        count = obj.enrollments.filter(role_in_course='STUDENT').count()
        return format_html('<span style="color: #007bff;">{} 👨‍🎓</span>', count)
    student_count.short_description = 'Học viên'
    
    def teacher_count(self, obj):
        count = obj.enrollments.filter(role_in_course='TEACHER').count()
        return format_html('<span style="color: #28a745;">{} 👨‍🏫</span>', count)
    teacher_count.short_description = 'Giảng viên'


class LessonInline(admin.TabularInline):
    """Inline Lesson in Module admin"""
    model = LessonModel
    extra = 1
    ordering = ['order']


@admin.register(ModuleModel, site=lms_admin_site)
class ModuleAdmin(admin.ModelAdmin):
    def get_changeform_initial_data(self, request):
        """Tự động set order mặc định khi tạo mới"""
        initial = super().get_changeform_initial_data(request)
        if 'order' not in initial or not initial.get('order'):
            # Lấy course từ request nếu có
            course_id = request.GET.get('course__id__exact')
            if course_id:
                from ..utils.order_manager import get_next_order
                queryset = ModuleModel.objects.filter(course_id=course_id)
                initial['order'] = get_next_order(queryset)
            else:
                initial['order'] = 1
        return initial
    list_display = ['title', 'course', 'order', 'lesson_count']
    list_filter = ['course', 'course__subject']
    search_fields = ['title', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [LessonInline]
    ordering = ['course', 'order']
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Số bài học'


class ResourceInline(admin.StackedInline):
    """Inline Resource in Lesson admin"""
    model = ResourceModel
    extra = 0
    ordering = ['order']
    fields = ['type', 'title', 'order', 'document_file', 'video_file', 'video_url', 'external_url', 'text_content', 'duration']
    classes = ['collapse']


class AssignmentInline(admin.TabularInline):
    """Inline Assignment in Lesson admin"""
    model = AssignmentModel
    extra = 0
    fields = ['title', 'type', 'start_at', 'end_at', 'attempts_allowed']


@admin.register(LessonModel, site=lms_admin_site)
class LessonAdmin(admin.ModelAdmin):
    def get_changeform_initial_data(self, request):
        """Tự động set order mặc định khi tạo mới"""
        initial = super().get_changeform_initial_data(request)
        if 'order' not in initial or not initial.get('order'):
            # Lấy module từ request nếu có
            module_id = request.GET.get('module__id__exact')
            if module_id:
                from ..utils.order_manager import get_next_order
                queryset = LessonModel.objects.filter(module_id=module_id)
                initial['order'] = get_next_order(queryset)
            else:
                initial['order'] = 1
        return initial
    list_display = ['title', 'module', 'order', 'resource_count', 'assignment_count']
    list_filter = ['module__course', 'module']
    search_fields = ['title', 'content', 'module__title']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ResourceInline, AssignmentInline]
    ordering = ['module', 'order']
    
    def resource_count(self, obj):
        return obj.resources.count()
    resource_count.short_description = 'Tài liệu'
    
    def assignment_count(self, obj):
        return obj.assignments.count()
    assignment_count.short_description = 'Bài tập'


# ==================== ENROLLMENT ADMIN ====================

@admin.register(EnrollmentModel, site=lms_admin_site)
class EnrollmentAdmin(admin.ModelAdmin):
    """
    Quản lý đăng ký khóa học
    
    ⚠️ LƯU Ý: Việc đăng ký khóa học chỉ được thực hiện bởi Admin.
    Sinh viên và giảng viên KHÔNG TỰ đăng ký trên hệ thống này.
    """
    list_display = ['user', 'get_user_fullname', 'course', 'get_course_status', 'role_in_course', 'joined_at']
    list_filter = ['role_in_course', 'course', 'course__subject', 'joined_at']
    search_fields = ['user__username', 'user__email', 'user__profile__full_name', 'course__title']
    readonly_fields = ['joined_at']
    autocomplete_fields = ['user', 'course']
    date_hierarchy = 'joined_at'
    list_per_page = 50
    
    fieldsets = (
        ('Thông tin đăng ký', {
            'fields': ('user', 'course', 'role_in_course'),
            'description': '⚠️ Chọn người dùng và khóa học để đăng ký'
        }),
        ('Thông tin hệ thống', {
            'fields': ('joined_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_fullname(self, obj):
        try:
            return obj.user.profile.full_name
        except:
            return obj.user.username
    get_user_fullname.short_description = 'Họ tên'
    get_user_fullname.admin_order_field = 'user__profile__full_name'
    
    def get_course_status(self, obj):
        status = obj.course.computed_status
        colors = {
            'UPCOMING': '#17a2b8',
            'ONGOING': '#28a745',
            'COMPLETED': '#6c757d',
        }
        icons = {
            'UPCOMING': '🔵',
            'ONGOING': '🟢',
            'COMPLETED': '⚫',
        }
        return format_html(
            '<span style="color: {};">{} {}</span>',
            colors.get(status, '#000'),
            icons.get(status, ''),
            obj.course.computed_status_display
        )
    get_course_status.short_description = 'Trạng thái khóa học'
    
    actions = ['set_role_student', 'set_role_teacher', 'set_role_ta']
    
    @admin.action(description='🎓 Đặt vai trò: Học viên')
    def set_role_student(self, request, queryset):
        updated = queryset.update(role_in_course='STUDENT')
        self.message_user(request, f'Đã cập nhật {updated} đăng ký thành Học viên.')
    
    @admin.action(description='👨‍🏫 Đặt vai trò: Giảng viên')
    def set_role_teacher(self, request, queryset):
        updated = queryset.update(role_in_course='TEACHER')
        self.message_user(request, f'Đã cập nhật {updated} đăng ký thành Giảng viên.')
    
    @admin.action(description='👨‍💼 Đặt vai trò: Trợ giảng')
    def set_role_ta(self, request, queryset):
        updated = queryset.update(role_in_course='TA')
        self.message_user(request, f'Đã cập nhật {updated} đăng ký thành Trợ giảng.')


# ==================== CONTENT ADMIN ====================

@admin.register(ResourceModel, site=lms_admin_site)
class ResourceAdmin(admin.ModelAdmin):
    """
    Quản lý tài liệu học tập
    
    Loại tài liệu:
    - DOCUMENT: Upload file từ máy (PDF, DOC, PPT, etc.)
    - VIDEO: Upload file HOẶC nhập URL (tự động tính thời lượng)
    - LINK: URL bên ngoài
    - TEXT: Nội dung văn bản
    """
    list_display = ['title', 'lesson', 'type', 'get_file_info', 'get_size', 'order', 'get_duration']
    list_filter = ['type', 'lesson__module__course', 'lesson__module']
    search_fields = ['title', 'lesson__title', 'lesson__module__course__title']
    readonly_fields = ['created_at', 'updated_at', 'file_size', 'duration', 'get_file_preview']
    ordering = ['lesson', 'order']
    autocomplete_fields = ['lesson']
    list_per_page = 30
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('lesson', 'type', 'title', 'order'),
        }),
        ('📄 Tài liệu (Document)', {
            'fields': ('document_file',),
            'classes': ('resource-document-fieldset',),
            'description': 'Upload tài liệu: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, TXT, ZIP, RAR (tối đa 20MB)'
        }),
        ('🎬 Video', {
            'fields': ('video_source', 'video_file', 'video_url', 'duration'),
            'classes': ('resource-video-fieldset',),
            'description': 'Chọn nguồn video: Upload file (MP4, WEBM, OGG, MOV, AVI, MKV, WMV, FLV, M4V - tối đa 500MB) HOẶC nhập URL (YouTube, Vimeo, etc.). Thời lượng sẽ tự động tính.'
        }),
        ('🔗 Liên kết', {
            'fields': ('external_url',),
            'classes': ('resource-link-fieldset',),
            'description': 'Nhập URL liên kết bên ngoài'
        }),
        ('📝 Văn bản', {
            'fields': ('text_content',),
            'classes': ('resource-text-fieldset',),
            'description': 'Nhập nội dung văn bản hiển thị trực tiếp'
        }),
        ('Thông tin file', {
            'fields': ('file_size', 'get_file_preview'),
            'classes': ('collapse',),
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    class Media:
        js = ('admin/js/resource_admin.js',)
    
    def get_changeform_initial_data(self, request):
        """Tự động set order mặc định khi tạo mới"""
        initial = super().get_changeform_initial_data(request)
        if 'order' not in initial or not initial.get('order'):
            # Lấy lesson từ request nếu có
            lesson_id = request.GET.get('lesson__id__exact')
            if lesson_id:
                from ..utils.order_manager import get_next_order
                queryset = ResourceModel.objects.filter(lesson_id=lesson_id)
                initial['order'] = get_next_order(queryset)
            else:
                initial['order'] = 1
        return initial
    
    def get_file_info(self, obj):
        """Hiển thị thông tin file/URL"""
        if obj.type == 'DOCUMENT':
            if obj.document_file:
                filename = obj.document_file.name.split('/')[-1]
                return format_html(
                    '<a href="{}" target="_blank">📄 {}</a>',
                    obj.document_file.url,
                    filename[:30] + '...' if len(filename) > 30 else filename
                )
            return format_html('<span style="color: red;">⚠️ Chưa upload</span>')
        
        elif obj.type == 'VIDEO':
            if obj.video_source == 'FILE' and obj.video_file:
                return format_html('🎬 <span style="color: green;">File đã upload</span>')
            elif obj.video_source == 'URL' and obj.video_url:
                return format_html(
                    '🔗 <a href="{}" target="_blank">URL Video</a>',
                    obj.video_url
                )
            return format_html('<span style="color: red;">⚠️ Chưa có video</span>')
        
        elif obj.type == 'LINK':
            if obj.external_url:
                return format_html(
                    '🔗 <a href="{}" target="_blank">{}</a>',
                    obj.external_url,
                    obj.external_url[:40] + '...' if len(obj.external_url) > 40 else obj.external_url
                )
            return format_html('<span style="color: red;">⚠️ Chưa có URL</span>')
        
        elif obj.type == 'TEXT':
            if obj.text_content:
                preview = obj.text_content[:50] + '...' if len(obj.text_content) > 50 else obj.text_content
                return format_html('📝 {}', preview)
            return format_html('<span style="color: red;">⚠️ Chưa có nội dung</span>')
        
        return '-'
    get_file_info.short_description = 'File/URL'
    
    def get_size(self, obj):
        """Hiển thị kích thước file"""
        if obj.file_size:
            return obj.file_size_display
        return '-'
    get_size.short_description = 'Kích thước'
    
    def get_duration(self, obj):
        """Hiển thị thời lượng video"""
        if obj.duration:
            return obj.duration_display
        return '-'
    get_duration.short_description = 'Thời lượng'
    
    def get_file_preview(self, obj):
        """Preview file"""
        if not obj or not obj.pk:
            return '-'
        
        if obj.type == 'DOCUMENT' and obj.document_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">📥 Tải xuống</a>',
                obj.document_file.url
            )
        elif obj.type == 'VIDEO':
            if obj.video_source == 'FILE' and obj.video_file:
                return format_html(
                    '<video width="320" height="240" controls style="max-width: 100%;">'
                    '<source src="{}" type="video/mp4">'
                    'Trình duyệt của bạn không hỗ trợ video tag.'
                    '</video>',
                    obj.video_file.url
                )
            elif obj.video_source == 'URL' and obj.video_url:
                try:
                    from src.infrastructure.services.youtube_utils import extract_youtube_video_id, is_youtube_url
                    
                    # Kiểm tra và extract YouTube video ID
                    if is_youtube_url(obj.video_url):
                        video_id = extract_youtube_video_id(obj.video_url)
                        if video_id:
                            embed_url = f"https://www.youtube.com/embed/{video_id}"
                            # Sử dụng mark_safe để render HTML
                            return mark_safe(
                                f'<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; margin: 10px 0;">'
                                f'<iframe width="100%" height="100%" src="{embed_url}" '
                                f'frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
                                f'allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>'
                                f'</div>'
                            )
                except Exception as e:
                    # Nếu có lỗi, hiển thị link
                    pass
                
                # Nếu không phải YouTube hoặc không extract được, hiển thị link
                return format_html(
                    '<a href="{}" target="_blank" class="button">🔗 Xem video</a>',
                    obj.video_url
                )
        return '-'
    get_file_preview.short_description = 'Xem trước'
    
    def save_model(self, request, obj, form, change):
        """Validate trước khi lưu"""
        obj.full_clean()
        super().save_model(request, obj, form, change)


# ==================== ASSESSMENT ADMIN ====================

class QuestionInline(admin.StackedInline):
    """
    Inline Question trong Assignment - Dạng Stacked để dễ nhập
    
    Admin có toàn quyền: thêm, sửa, xóa câu hỏi inline.
    """
    model = QuestionModel
    extra = 0
    ordering = ['order']
    fields = ['order', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'points', 'explanation']
    classes = ['collapse']
    verbose_name = 'Câu hỏi'
    verbose_name_plural = 'Danh sách câu hỏi'
    
    def has_add_permission(self, request, obj=None):
        """Admin có quyền thêm câu hỏi inline"""
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        """Admin có quyền sửa câu hỏi inline"""
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        """Admin có quyền xóa câu hỏi inline"""
        return request.user.is_staff


@admin.register(AssignmentModel, site=lms_admin_site)
class AssignmentAdmin(admin.ModelAdmin):
    """
    Quản lý bài tập Quiz
    
    Chức năng:
    1. Tạo/sửa/xóa bài tập Quiz (Admin có toàn quyền)
    2. Thêm/sửa/xóa câu hỏi trực tiếp (inline)
    3. Import câu hỏi từ Excel (custom view)
    4. Xem thống kê: số câu hỏi, số lần làm, trạng thái
    
    Loại bài tập:
    - QUIZ: Bài kiểm tra trắc nghiệm (có câu hỏi)
    - FILE_UPLOAD: Nộp file bài tập
    """
    list_display = ['title', 'lesson', 'type', 'get_status', 'question_count', 'start_at', 'end_at', 'attempts_allowed', 'attempt_count']
    list_filter = ['type', 'lesson__module__course', 'start_at']
    search_fields = ['title', 'lesson__title', 'lesson__module__course__title']
    readonly_fields = ['created_at', 'updated_at', 'get_import_info']
    autocomplete_fields = ['lesson']
    date_hierarchy = 'start_at'
    inlines = [QuestionInline]
    
    def has_add_permission(self, request):
        """Admin có quyền thêm"""
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        """Admin có quyền sửa"""
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        """Admin có quyền xóa"""
        return request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        """Admin có quyền xem"""
        return request.user.is_staff
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('lesson', 'title', 'instructions', 'type')
        }),
        ('Cài đặt thời gian', {
            'fields': ('start_at', 'end_at', 'time_limit', 'attempts_allowed', 'max_score')
        }),
        ('Cài đặt Quiz', {
            'fields': ('shuffle_questions', 'shuffle_answers', 'show_result'),
            'classes': ('collapse',),
            'description': 'Các tùy chọn cho bài kiểm tra trắc nghiệm'
        }),
        ('📥 Import Excel', {
            'fields': ('get_import_info',),
            'classes': ('collapse',),
            'description': 'Hướng dẫn import câu hỏi từ Excel. Click nút "Import Excel" ở trên cùng trang này.'
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        """Thêm custom URL cho import Excel"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:assignment_id>/import-excel/',
                self.admin_site.admin_view(self.import_excel_view),
                name='persistence_assignmentmodel_import_excel',
            ),
        ]
        return custom_urls + urls
    
    def import_excel_view(self, request, assignment_id):
        """
        Custom view để import Excel
        
        Chỉ admin (is_staff) mới được truy cập.
        """
        from django.shortcuts import render, redirect, get_object_or_404
        from django import forms
        from django.contrib import messages
        from django.core.exceptions import PermissionDenied
        
        # Kiểm tra quyền admin
        if not request.user.is_staff:
            raise PermissionDenied("Chỉ admin mới có quyền import câu hỏi")
        
        assignment = get_object_or_404(AssignmentModel, pk=assignment_id)
        
        class ExcelUploadForm(forms.Form):
            file = forms.FileField(
                label='File Excel (.xlsx hoặc .xls)',
                help_text='File Excel chứa danh sách câu hỏi',
                widget=forms.FileInput(attrs={'accept': '.xlsx,.xls', 'class': 'fileinput'})
            )
        
        if request.method == 'POST':
            form = ExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES['file']
                
                try:
                    # Parse Excel
                    from src.infrastructure.services.excel_parser import ExcelQuestionParser
                    parser = ExcelQuestionParser()
                    questions_data = parser.parse(file, file.name)
                    
                    if not questions_data:
                        messages.error(request, 'File Excel không có dữ liệu câu hỏi.')
                    else:
                        # Import questions
                        from ...application.use_cases.assessment import (
                            ImportQuestionsInput,
                            ImportQuestionsFromExcelUseCase
                        )
                        
                        use_case = ImportQuestionsFromExcelUseCase()
                        result = use_case.execute(ImportQuestionsInput(
                            assignment_id=assignment.id,
                            user_id=request.user.id,
                            questions_data=questions_data,
                        ))
                        
                        # Hiển thị kết quả
                        if result.error_rows:
                            error_msg = f"Import hoàn tất với {len(result.error_rows)} lỗi:\n"
                            for err in result.error_rows[:5]:
                                error_msg += f"  • Dòng {err['row']}: {err['error']}\n"
                            if len(result.error_rows) > 5:
                                error_msg += f"  ... và {len(result.error_rows) - 5} lỗi khác"
                            messages.warning(request, error_msg)
                        
                        messages.success(
                            request,
                            f'Đã import thành công {result.success_count}/{result.total_rows} câu hỏi vào bài tập "{assignment.title}"'
                        )
                        
                        # Redirect về trang edit assignment
                        return redirect(f'/admin/persistence/assignmentmodel/{assignment.id}/change/')
                        
                except Exception as e:
                    messages.error(request, f'Lỗi khi import: {str(e)}')
        else:
            form = ExcelUploadForm()
        
        context = {
            **self.admin_site.each_context(request),
            'title': f'Import câu hỏi cho: {assignment.title}',
            'assignment': assignment,
            'form': form,
            'opts': self.model._meta,
            'has_view_permission': True,
            'original': assignment,
        }
        
        return render(request, 'admin/import_excel.html', context)
    
    def get_status(self, obj):
        if obj.is_open:
            return format_html('<span style="color: green;">🟢 Đang mở</span>')
        elif obj.is_upcoming:
            return format_html('<span style="color: blue;">🔵 Chưa mở</span>')
        else:
            return format_html('<span style="color: gray;">⚫ Đã đóng</span>')
    get_status.short_description = 'Trạng thái'
    
    def question_count(self, obj):
        count = obj.questions.count()
        if count > 0:
            return format_html('<span style="color: green; font-weight: bold;">{} câu</span>', count)
        return format_html('<span style="color: gray;">-</span>')
    question_count.short_description = 'Câu hỏi'
    
    def attempt_count(self, obj):
        count = obj.attempts.count()
        if count > 0:
            return format_html('<span style="color: blue;">{} lần</span>', count)
        return format_html('<span style="color: gray;">0</span>')
    attempt_count.short_description = 'Lần làm'
    
    def get_import_info(self, obj):
        """Hiển thị hướng dẫn import Excel và nút import"""
        if obj.pk:
            import_url = f'/admin/persistence/assignmentmodel/{obj.pk}/import-excel/'
            button = format_html(
                '<a href="{}" class="button" style="margin-top: 10px; display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">📥 Import từ Excel</a>',
                import_url
            )
        else:
            button = format_html('<p style="color: #999;">Lưu bài tập trước để import câu hỏi</p>')
        
        return format_html(
            '<div style="padding: 10px; background: #f0f0f0; border-radius: 5px;">'
            '<strong>📋 Format Excel:</strong><br>'
            'Cột 1: text (Nội dung câu hỏi)<br>'
            'Cột 2: A (Đáp án A)<br>'
            'Cột 3: B (Đáp án B)<br>'
            'Cột 4: C (Đáp án C)<br>'
            'Cột 5: D (Đáp án D)<br>'
            'Cột 6: correct (Đáp án đúng: A/B/C/D)<br>'
            'Cột 7: explanation (Giải thích - tùy chọn)<br>'
            'Cột 8: points (Điểm - tùy chọn, mặc định 1)<br><br>'
            '{}'
            '</div>',
            button
        )
    get_import_info.short_description = 'Import Excel'


@admin.register(QuestionModel, site=lms_admin_site)
class QuestionAdmin(admin.ModelAdmin):
    """
    Quản lý câu hỏi trắc nghiệm
    
    Admin có toàn quyền: thêm, sửa, xóa câu hỏi.
    """
    list_display = ['get_short_text', 'assignment', 'correct_answer', 'points', 'order']
    list_filter = ['correct_answer', 'assignment__lesson__module__course', 'assignment']
    search_fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'explanation']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['assignment', 'order']
    list_per_page = 50
    
    def has_add_permission(self, request):
        """Admin có quyền thêm"""
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        """Admin có quyền sửa"""
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        """Admin có quyền xóa"""
        return request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        """Admin có quyền xem"""
        return request.user.is_staff
    
    fieldsets = (
        ('Bài tập', {
            'fields': ('assignment', 'order', 'points')
        }),
        ('Nội dung câu hỏi', {
            'fields': ('text',)
        }),
        ('Đáp án', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
        }),
        ('Giải thích', {
            'fields': ('explanation',),
            'classes': ('collapse',)
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_short_text(self, obj):
        text = obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
        return text
    get_short_text.short_description = 'Câu hỏi'
    
    def get_changeform_initial_data(self, request):
        """Tự động set order mặc định khi tạo mới"""
        initial = super().get_changeform_initial_data(request)
        if 'order' not in initial or not initial.get('order'):
            # Lấy assignment từ request nếu có
            assignment_id = request.GET.get('assignment__id__exact')
            if assignment_id:
                from ..utils.order_manager import get_next_order
                queryset = QuestionModel.objects.filter(assignment_id=assignment_id)
                initial['order'] = get_next_order(queryset)
            else:
                initial['order'] = 1
        return initial


class AttemptDetailInline(admin.TabularInline):
    """Inline AttemptDetail trong Attempt"""
    model = AttemptDetailModel
    extra = 0
    readonly_fields = ['question', 'chosen_answer', 'is_correct']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AttemptModel, site=lms_admin_site)
class AttemptAdmin(admin.ModelAdmin):
    """
    Quản lý lần làm bài của học viên
    
    Admin có toàn quyền: xem, chấm điểm, thêm feedback.
    """
    list_display = ['user', 'assignment', 'status', 'get_result', 'score', 'started_at', 'submitted_at']
    list_filter = ['status', 'assignment__lesson__module__course', 'started_at']
    search_fields = ['user__username', 'user__profile__full_name', 'assignment__title']
    readonly_fields = ['started_at', 'user', 'assignment', 'get_quiz_result']
    date_hierarchy = 'started_at'
    list_per_page = 50
    inlines = [AttemptDetailInline]
    
    def has_add_permission(self, request):
        """Admin có thể thêm attempt (nếu cần)"""
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        """Admin có quyền sửa (chấm điểm, feedback)"""
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        """Admin có quyền xóa"""
        return request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        """Admin có quyền xem"""
        return request.user.is_staff
    
    fieldsets = (
        ('Thông tin', {
            'fields': ('user', 'assignment', 'status')
        }),
        ('Kết quả Quiz', {
            'fields': ('get_quiz_result',),
            'classes': ('collapse',),
            'description': 'Kết quả chi tiết cho bài kiểm tra trắc nghiệm'
        }),
        ('Bài nộp (File Upload)', {
            'fields': ('submitted_file', 'submitted_text', 'submitted_at'),
            'classes': ('collapse',),
            'description': 'File nộp bài: PDF, DOC, DOCX, PPT, XLS, ZIP, RAR, JPG, PNG, PY, JAVA, etc. (tối đa 50MB)'
        }),
        ('Chấm điểm', {
            'fields': ('score', 'feedback')
        }),
        ('Thời gian', {
            'fields': ('started_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_result(self, obj):
        try:
            if obj.assignment and obj.assignment.type == 'QUIZ' and obj.total_questions > 0:
                return format_html(
                    '<span>{}/{} ({:.0f}%)</span>',
                    obj.correct_count,
                    obj.total_questions,
                    (obj.correct_count / obj.total_questions) * 100
                )
        except Exception:
            pass
        return '-'
    get_result.short_description = 'Kết quả'
    
    def get_quiz_result(self, obj):
        try:
            if obj.assignment and obj.assignment.type == 'QUIZ':
                return format_html(
                    '<strong>Đúng:</strong> {}/{} câu<br>'
                    '<strong>Tỷ lệ:</strong> {:.1f}%<br>'
                    '<strong>Điểm tự động:</strong> {:.2f}',
                    obj.correct_count,
                    obj.total_questions,
                    (obj.correct_count / obj.total_questions * 100) if obj.total_questions > 0 else 0,
                    obj.calculate_score()
                )
        except Exception:
            pass
        return 'Không phải bài Quiz'
    get_quiz_result.short_description = 'Kết quả Quiz'
    
    actions = ['mark_as_graded', 'auto_grade_quiz']
    
    @admin.action(description='✅ Đánh dấu đã chấm điểm')
    def mark_as_graded(self, request, queryset):
        updated = queryset.filter(status='SUBMITTED').update(status='GRADED')
        self.message_user(request, f'Đã đánh dấu {updated} bài đã chấm điểm.')
    
    @admin.action(description='🤖 Tự động chấm điểm Quiz')
    def auto_grade_quiz(self, request, queryset):
        count = 0
        for attempt in queryset.filter(assignment__type='QUIZ', status='SUBMITTED'):
            attempt.score = attempt.calculate_score()
            attempt.status = 'GRADED'
            attempt.save()
            count += 1
        self.message_user(request, f'Đã tự động chấm điểm {count} bài Quiz.')


@admin.register(AttemptDetailModel, site=lms_admin_site)
class AttemptDetailAdmin(admin.ModelAdmin):
    """
    Xem chi tiết câu trả lời
    """
    list_display = ['attempt', 'get_question_text', 'chosen_answer', 'get_correct_answer', 'is_correct']
    list_filter = ['is_correct', 'attempt__assignment', 'attempt__user']
    search_fields = ['attempt__user__username', 'question__text']
    readonly_fields = ['attempt', 'question', 'chosen_answer', 'is_correct']
    list_per_page = 100
    
    def get_question_text(self, obj):
        text = obj.question.text[:40] + '...' if len(obj.question.text) > 40 else obj.question.text
        return f"Q{obj.question.order}: {text}"
    get_question_text.short_description = 'Câu hỏi'
    
    def get_correct_answer(self, obj):
        return obj.question.correct_answer
    get_correct_answer.short_description = 'Đáp án đúng'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# ==================== ACTIVITY ADMIN ====================

@admin.register(UserActivityLogModel, site=lms_admin_site)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'target_type', 'target_id', 'timestamp']
    list_filter = ['action_type', 'target_type', 'timestamp']
    search_fields = ['user__username']
    readonly_fields = ['user', 'action_type', 'target_type', 'target_id', 'metadata', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# ==================== COMMUNICATION ADMIN ====================

@admin.register(NotificationModel, site=lms_admin_site)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'type', 'is_read', 'related_object_type', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read']
    
    @admin.action(description='✅ Đánh dấu đã đọc')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'Đã đánh dấu {updated} thông báo đã đọc.')


class CommentReplyInline(admin.TabularInline):
    """Inline replies in Comment admin"""
    model = CommentModel
    fk_name = 'parent'
    extra = 0
    readonly_fields = ['user', 'content', 'created_at']
    can_delete = False
    verbose_name = 'Trả lời'
    verbose_name_plural = 'Các trả lời'


@admin.register(CommentModel, site=lms_admin_site)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_type', 'target_id', 'short_content', 'parent', 'created_at']
    list_filter = ['target_type', 'created_at']
    search_fields = ['user__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CommentReplyInline]
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Nội dung'


# ==================== ADMIN SITE CUSTOMIZATION ====================

admin.site.site_header = '🎓 LMS Admin'
admin.site.site_title = 'LMS Admin Portal'
admin.site.index_title = 'Quản lý hệ thống học trực tuyến'
