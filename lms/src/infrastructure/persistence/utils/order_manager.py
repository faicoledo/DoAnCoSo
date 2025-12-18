"""
Order Manager Utility

Quản lý thứ tự (order) cho các model:
- Tự động gán order mới = max + 1 khi tạo mới
- Hoán đổi order nếu order đã tồn tại
- Sắp xếp lại order khi xóa (luôn tuần tự)
"""
from django.db import models
from django.db.models import Max, Q


def get_next_order(queryset, order_field='order'):
    """
    Lấy order tiếp theo (max + 1)
    
    Args:
        queryset: QuerySet để tìm max order
        order_field: Tên field order (mặc định 'order')
    
    Returns:
        int: Order tiếp theo
    """
    max_order = queryset.aggregate(max_order=Max(order_field))['max_order']
    return (max_order or 0) + 1


def handle_order_on_save(instance, parent_field, order_field='order'):
    """
    Xử lý order khi save:
    - Tạo mới: Tự động gán max + 1 nếu chưa có order
    - Update: Hoán đổi nếu order đã tồn tại
    
    Args:
        instance: Model instance
        parent_field: Tên field parent (ví dụ: 'assignment', 'course', 'module', 'lesson')
        order_field: Tên field order (mặc định 'order')
    """
    if not hasattr(instance, parent_field) or not hasattr(instance, order_field):
        return
    
    parent = getattr(instance, parent_field)
    if not parent:
        return  # Chưa có parent, không thể xử lý
    
    # Lấy queryset của các instance cùng parent
    model_class = instance.__class__
    queryset = model_class.objects.filter(**{parent_field: parent})
    
    # Nếu đang update, loại trừ chính instance này
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)
    
    new_order = getattr(instance, order_field)
    old_order = None
    
    # Lấy order cũ nếu đang update
    if instance.pk:
        try:
            old_instance = model_class.objects.get(pk=instance.pk)
            old_order = getattr(old_instance, order_field)
        except model_class.DoesNotExist:
            pass
    
    # Nếu tạo mới và chưa có order hoặc order = 0, tự động gán max + 1
    if instance._state.adding:
        if not new_order or new_order == 0:
            new_order = get_next_order(queryset, order_field)
            setattr(instance, order_field, new_order)
            return  # Không cần kiểm tra trùng vì đã là max + 1
    
    # Kiểm tra xem order có trùng không
    existing = queryset.filter(**{order_field: new_order}).first()
    
    if existing:
        # Hoán đổi: instance cũ lấy order của instance mới
        if old_order and old_order != new_order:
            # Hoán đổi: existing lấy old_order
            setattr(existing, order_field, old_order)
            existing.save(update_fields=[order_field])
        else:
            # Nếu không có order cũ (tạo mới với order đã tồn tại)
            # Tìm order tiếp theo không trùng
            next_order = new_order + 1
            while queryset.filter(**{order_field: next_order}).exists():
                next_order += 1
            setattr(existing, order_field, next_order)
            existing.save(update_fields=[order_field])


def handle_order_on_delete(instance, parent_field, order_field='order'):
    """
    Sắp xếp lại order khi xóa:
    - Tất cả order > order bị xóa sẽ giảm 1
    
    Args:
        instance: Model instance đang bị xóa
        parent_field: Tên field parent
        order_field: Tên field order
    """
    if not hasattr(instance, parent_field) or not hasattr(instance, order_field):
        return
    
    parent = getattr(instance, parent_field)
    if not parent:
        return
    
    deleted_order = getattr(instance, order_field)
    if not deleted_order:
        return
    
    # Lấy tất cả instance cùng parent có order > deleted_order
    model_class = instance.__class__
    queryset = model_class.objects.filter(
        **{
            parent_field: parent,
            f'{order_field}__gt': deleted_order
        }
    )
    
    # Giảm order của tất cả instance có order > deleted_order
    for obj in queryset:
        current_order = getattr(obj, order_field)
        setattr(obj, order_field, current_order - 1)
        obj.save(update_fields=[order_field])


def normalize_orders(queryset, order_field='order'):
    """
    Chuẩn hóa order để luôn tuần tự từ 1, 2, 3, ...
    
    Args:
        queryset: QuerySet cần chuẩn hóa
        order_field: Tên field order
    """
    objects = list(queryset.order_by(order_field))
    for idx, obj in enumerate(objects, start=1):
        current_order = getattr(obj, order_field)
        if current_order != idx:
            setattr(obj, order_field, idx)
            obj.save(update_fields=[order_field])

