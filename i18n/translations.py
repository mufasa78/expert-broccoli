# Translation dictionary for the application
TRANSLATIONS = {
    'en': {
        # General
        'app_title': 'Chinese License Plate Recognition & Lane Intrusion Detection',
        'app_description': 'A detection system based on YOLOv8 for Chinese license plates and lane intrusion at intersections.',
        
        # Navigation
        'home': 'Home',
        'api': 'API',
        'about': 'About',
        
        # Detection types
        'license_plate_recognition': 'License Plate Recognition',
        'license_plate_detection': 'License Plate Detection',
        'lane_intrusion_detection': 'Lane Intrusion Detection',
        
        # License plate tab
        'license_plate_tab': 'License Plate Recognition',
        'license_plate_description': 'This module detects and recognizes Chinese license plates in images and videos.',
        
        # Lane intrusion tab
        'lane_intrusion_tab': 'Lane Intrusion Detection',
        'lane_intrusion_description': 'This module detects vehicles crossing lanes at intersections, which may indicate traffic violations.',
        
        # Upload
        'upload_image_video': 'Upload Image or Video',
        'browse_files': 'Browse Files',
        'drag_drop': 'Drag and drop files here or click to browse',
        'supported_formats': 'Supported formats: .jpg, .jpeg, .png, .mp4, .avi',
        
        # Processing
        'process_image': 'Process Image',
        'process_video': 'Process Video',
        'processing': 'Processing...',
        'upload_and_detect': 'Upload & Detect',
        
        # Results
        'detection_results': 'Detection Results',
        'no_results': 'No results found',
        'processing_stats': 'Processing Statistics',
        'processing_results': 'Processing Results',
        'elapsed_time': 'Elapsed Time',
        'processed_frames': 'Processed Frames',
        'total_frames': 'Total Frames',
        'detected_plates': 'Detected Plates',
        'processing_time': 'Processing Time',
        'intrusion_events': 'Intrusion Events',
        'processed_image': 'Processed Image',
        'uploaded_image': 'Uploaded Image',
        'download_result': 'Download Result',
        'vehicles_detected': 'Vehicles Detected',
        'vehicles': 'vehicles',
        
        # Video processing
        'processing_frame': 'Processing Frame',
        'frame': 'Frame',
        'video_processing_complete': 'Video Processing Complete',
        'view_all_detections': 'View All License Plate Detections',
        'view_all_intrusions': 'View All Intrusion Events',
        
        # Plates
        'plate': 'Plate',
        'confidence': 'Confidence',
        'no_plates_found': 'No license plates found',
        
        # Lane intrusion
        'vehicle': 'Vehicle',
        'lane': 'Lane',
        'no_lane': 'No Lane',
        'no_intrusions_detected': 'No lane intrusions detected',
        
        # Errors
        'error': 'Error',
        'no_file_error': 'No file provided',
        'no_file_selected_error': 'No file selected',
        'processing_error': 'Processing error',
        'invalid_file_error': 'Invalid file type'
    },
    'zh': {
        # General
        'app_title': '中国车牌识别与车道入侵检测系统',
        'app_description': '基于YOLOv8的中国车牌识别和十字路口车道入侵检测系统。',
        
        # Navigation
        'home': '首页',
        'api': 'API接口',
        'about': '关于',
        
        # Detection types
        'license_plate_recognition': '车牌识别',
        'license_plate_detection': '车牌检测',
        'lane_intrusion_detection': '车道入侵检测',
        
        # License plate tab
        'license_plate_tab': '车牌识别',
        'license_plate_description': '此模块可检测并识别图像和视频中的中国车牌。',
        
        # Lane intrusion tab
        'lane_intrusion_tab': '车道入侵检测',
        'lane_intrusion_description': '此模块检测十字路口处穿越车道的车辆，这可能表示交通违规行为。',
        
        # Upload
        'upload_image_video': '上传图像或视频',
        'browse_files': '浏览文件',
        'drag_drop': '将文件拖放到此处或点击浏览',
        'supported_formats': '支持的格式: .jpg, .jpeg, .png, .mp4, .avi',
        
        # Processing
        'process_image': '处理图像',
        'process_video': '处理视频',
        'processing': '处理中...',
        'upload_and_detect': '上传并检测',
        
        # Results
        'detection_results': '检测结果',
        'no_results': '未找到结果',
        'processing_stats': '处理统计',
        'processing_results': '处理结果',
        'elapsed_time': '已用时间',
        'processed_frames': '已处理帧数',
        'total_frames': '总帧数',
        'detected_plates': '检测到的车牌',
        'processing_time': '处理时间',
        'intrusion_events': '入侵事件',
        'processed_image': '处理后的图像',
        'uploaded_image': '上传的图像',
        'download_result': '下载结果',
        'vehicles_detected': '检测到的车辆',
        'vehicles': '辆车',
        
        # Video processing
        'processing_frame': '正在处理帧',
        'frame': '帧',
        'video_processing_complete': '视频处理完成',
        'view_all_detections': '查看所有车牌检测结果',
        'view_all_intrusions': '查看所有入侵事件',
        
        # Plates
        'plate': '车牌',
        'confidence': '置信度',
        'no_plates_found': '未检测到车牌',
        
        # Lane intrusion
        'vehicle': '车辆',
        'lane': '车道',
        'no_lane': '无车道',
        'no_intrusions_detected': '未检测到车道入侵',
        
        # Errors
        'error': '错误',
        'no_file_error': '未提供文件',
        'no_file_selected_error': '未选择文件',
        'processing_error': '处理错误',
        'invalid_file_error': '无效的文件类型'
    }
}

def get_text(key, lang='zh'):
    """
    Get translated text for a key
    
    Args:
        key: Translation key
        lang: Language code ('zh' or 'en')
        
    Returns:
        Translated text
    """
    if lang not in TRANSLATIONS:
        lang = 'zh'  # Default to Chinese
    
    if key not in TRANSLATIONS[lang]:
        # Return key if translation not found
        return key
    
    return TRANSLATIONS[lang][key]
