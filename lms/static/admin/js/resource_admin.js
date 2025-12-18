/**
 * Resource Admin JavaScript
 * 
 * Ẩn/hiện fields động dựa trên loại tài liệu được chọn
 */
(function($) {
    'use strict';
    
    function toggleResourceFields() {
        var type = $('#id_type').val();
        var videoSource = $('#id_video_source').val();
        
        // Ẩn tất cả fieldsets trước
        $('.resource-document-fieldset').hide();
        $('.resource-video-fieldset').hide();
        $('.resource-link-fieldset').hide();
        $('.resource-text-fieldset').hide();
        
        // Hiển thị fieldset tương ứng
        if (type === 'DOCUMENT') {
            $('.resource-document-fieldset').show();
        } else if (type === 'VIDEO') {
            $('.resource-video-fieldset').show();
            toggleVideoSourceFields(videoSource);
        } else if (type === 'LINK') {
            $('.resource-link-fieldset').show();
        } else if (type === 'TEXT') {
            $('.resource-text-fieldset').show();
        }
    }
    
    function toggleVideoSourceFields(videoSource) {
        // Ẩn cả hai field
        $('#id_video_file').closest('.form-row, .field-video_file').hide();
        $('#id_video_url').closest('.form-row, .field-video_url').hide();
        
        // Hiển thị field tương ứng
        if (videoSource === 'FILE') {
            $('#id_video_file').closest('.form-row, .field-video_file').show();
        } else if (videoSource === 'URL') {
            $('#id_video_url').closest('.form-row, .field-video_url').show();
        }
    }
    
    $(document).ready(function() {
        // Khởi tạo khi trang load
        toggleResourceFields();
        
        // Lắng nghe thay đổi loại tài liệu
        $('#id_type').on('change', function() {
            toggleResourceFields();
        });
        
        // Lắng nghe thay đổi nguồn video
        $('#id_video_source').on('change', function() {
            toggleVideoSourceFields($(this).val());
        });
    });
    
})(django.jQuery);




