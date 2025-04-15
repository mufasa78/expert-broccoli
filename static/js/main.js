// Main JavaScript functionality for the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupFileUpload();
    setupLanguageToggle();
    setupDetectionOptions();
    setupVideoProcessing();
}

// Configure the file upload functionality
function setupFileUpload() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const uploadPreview = document.getElementById('uploadPreview');
    const progressBar = document.getElementById('uploadProgressBar');
    const progressContainer = document.getElementById('progressContainer');
    
    if (!uploadForm || !fileInput) return;
    
    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        uploadArea.classList.add('bg-light');
    }
    
    function unhighlight() {
        uploadArea.classList.remove('bg-light');
    }
    
    // Handle file drop
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            updateFilePreview(files[0]);
        }
    }
    
    // Preview file when selected via input
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            updateFilePreview(this.files[0]);
        }
    });
    
    // Preview the selected file
    function updateFilePreview(file) {
        // Clear previous preview
        uploadPreview.innerHTML = '';
        uploadPreview.style.display = 'block';
        
        // Check if the file is an image or video
        if (file.type.match('image.*')) {
            const img = document.createElement('img');
            img.classList.add('img-fluid', 'mt-3', 'rounded');
            img.file = file;
            
            uploadPreview.appendChild(img);
            
            const reader = new FileReader();
            reader.onload = (function(aImg) {
                return function(e) {
                    aImg.src = e.target.result;
                };
            })(img);
            
            reader.readAsDataURL(file);
        } else if (file.type.match('video.*')) {
            const video = document.createElement('video');
            video.classList.add('img-fluid', 'mt-3', 'rounded');
            video.controls = true;
            
            uploadPreview.appendChild(video);
            
            const reader = new FileReader();
            reader.onload = (function(aVideo) {
                return function(e) {
                    aVideo.src = e.target.result;
                };
            })(video);
            
            reader.readAsDataURL(file);
        } else {
            // Unsupported file type
            const unsupportedMsg = document.createElement('div');
            unsupportedMsg.classList.add('alert', 'alert-warning', 'mt-3');
            unsupportedMsg.textContent = getTranslatedText('unsupported_file_type');
            uploadPreview.appendChild(unsupportedMsg);
        }
    }
    
    // Show upload progress
    uploadForm.addEventListener('submit', function() {
        // Show progress bar for visual feedback
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';
        
        // Simulate progress (since we can't track actual form submit progress easily)
        let progress = 0;
        const progressInterval = setInterval(function() {
            progress += 5;
            progressBar.style.width = Math.min(progress, 90) + '%';
            
            if (progress >= 90) {
                clearInterval(progressInterval);
            }
        }, 100);
    });
}

// Setup language toggle functionality
function setupLanguageToggle() {
    const langToggle = document.getElementById('languageToggle');
    if (!langToggle) return;
    
    langToggle.addEventListener('change', function() {
        const langForm = document.getElementById('languageForm');
        if (langForm) {
            langForm.submit();
        }
    });
}

// Setup detection type radio buttons
function setupDetectionOptions() {
    const detectionOptions = document.querySelectorAll('input[name="detection_type"]');
    if (detectionOptions.length === 0) return;
    
    detectionOptions.forEach(option => {
        option.addEventListener('change', function() {
            updateDetectionDescription(this.value);
        });
    });
    
    // Initialize with the checked option
    const checkedOption = document.querySelector('input[name="detection_type"]:checked');
    if (checkedOption) {
        updateDetectionDescription(checkedOption.value);
    }
}

// Update the description based on selected detection type
function updateDetectionDescription(detectionType) {
    const descriptionElement = document.getElementById('detectionDescription');
    if (!descriptionElement) return;
    
    let description;
    
    if (detectionType === 'license_plate') {
        description = getTranslatedText('license_plate_description');
    } else if (detectionType === 'lane_intrusion') {
        description = getTranslatedText('lane_intrusion_description');
    } else {
        description = '';
    }
    
    descriptionElement.innerHTML = description;
    descriptionElement.classList.add('fade-in');
    
    // Reset animation
    setTimeout(() => {
        descriptionElement.classList.remove('fade-in');
    }, 500);
}

// Setup video processing functionality
function setupVideoProcessing() {
    const processVideoBtn = document.getElementById('processVideoBtn');
    const videoResults = document.getElementById('videoResults');
    const videoProgressContainer = document.getElementById('videoProgressContainer');
    const videoProgressBar = document.getElementById('videoProgressBar');
    
    if (!processVideoBtn) return;
    
    processVideoBtn.addEventListener('click', function() {
        const filepath = this.getAttribute('data-filepath');
        const detectionType = this.getAttribute('data-detection-type');
        
        if (!filepath) return;
        
        // Show progress
        videoProgressContainer.style.display = 'block';
        videoProgressBar.style.width = '0%';
        videoResults.innerHTML = '<div class="text-center mt-3"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">' + getTranslatedText('processing_video') + '</p></div>';
        
        // Process the video via AJAX
        const formData = new FormData();
        formData.append('filepath', filepath);
        formData.append('detection_type', detectionType);
        
        fetch('/process_video', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                videoResults.innerHTML = '<div class="alert alert-danger">' + data.error + '</div>';
                return;
            }
            
            videoResults.innerHTML = '';
            
            // Create results summary
            const summary = document.createElement('div');
            summary.classList.add('alert', 'alert-info', 'mt-3');
            summary.innerHTML = `
                <h4>${getTranslatedText('processing_complete')}</h4>
                <p>${getTranslatedText('processed_frames')}: ${data.processed_frames}/${data.total_frames}</p>
                <p>${getTranslatedText('detections_found')}: ${data.detections_count}</p>
            `;
            videoResults.appendChild(summary);
            
            // Show frames with detections
            const detectionsContainer = document.createElement('div');
            detectionsContainer.classList.add('row', 'mt-3');
            
            data.results.forEach(result => {
                if (result.detections && result.detections.length > 0 || result.intrusions && result.intrusions.length > 0) {
                    const col = document.createElement('div');
                    col.classList.add('col-md-6', 'mb-3');
                    
                    const card = document.createElement('div');
                    card.classList.add('card');
                    
                    // Card header with frame info
                    const cardHeader = document.createElement('div');
                    cardHeader.classList.add('card-header');
                    cardHeader.textContent = `${getTranslatedText('frame')} ${result.frame}`;
                    
                    // Card body with image and detections
                    const cardBody = document.createElement('div');
                    cardBody.classList.add('card-body');
                    
                    // Add the frame image
                    const img = document.createElement('img');
                    img.classList.add('img-fluid', 'rounded', 'mb-2');
                    img.src = '/static/' + result.frame_path;
                    
                    cardBody.appendChild(img);
                    
                    // Add detection/intrusion info
                    if (detectionType === 'license_plate' && result.detections) {
                        const detectionInfo = document.createElement('div');
                        detectionInfo.classList.add('mt-2');
                        
                        result.detections.forEach((detection, index) => {
                            if (detection.license_plate) {
                                const plateDiv = document.createElement('div');
                                plateDiv.classList.add('license-plate', 'mb-2');
                                plateDiv.textContent = detection.license_plate;
                                detectionInfo.appendChild(plateDiv);
                            }
                        });
                        
                        cardBody.appendChild(detectionInfo);
                    }
                    
                    if (detectionType === 'lane_intrusion' && result.intrusions) {
                        const intrusionInfo = document.createElement('div');
                        intrusionInfo.classList.add('mt-2');
                        
                        result.intrusions.forEach((intrusion, index) => {
                            const intrusionDiv = document.createElement('div');
                            intrusionDiv.classList.add('alert', 'alert-danger', 'mb-2', 'py-1');
                            intrusionDiv.textContent = `${getTranslatedText('vehicle')} ${intrusion.vehicle_id}: ${getTranslatedText('lane')} ${intrusion.from_lane + 1} → ${intrusion.to_lane + 1}`;
                            intrusionInfo.appendChild(intrusionDiv);
                        });
                        
                        cardBody.appendChild(intrusionInfo);
                    }
                    
                    card.appendChild(cardHeader);
                    card.appendChild(cardBody);
                    col.appendChild(card);
                    detectionsContainer.appendChild(col);
                }
            });
            
            if (detectionsContainer.children.length === 0) {
                const noDetections = document.createElement('div');
                noDetections.classList.add('alert', 'alert-warning');
                noDetections.textContent = getTranslatedText('no_detections_found');
                detectionsContainer.appendChild(noDetections);
            }
            
            videoResults.appendChild(detectionsContainer);
            
            // Hide progress bar when complete
            videoProgressContainer.style.display = 'none';
        })
        .catch(error => {
            console.error('Error:', error);
            videoResults.innerHTML = '<div class="alert alert-danger">' + getTranslatedText('processing_error') + ': ' + error.message + '</div>';
            videoProgressContainer.style.display = 'none';
        });
        
        // Update progress bar
        let progress = 0;
        const progressInterval = setInterval(function() {
            progress += 2;
            videoProgressBar.style.width = Math.min(progress, 100) + '%';
            
            if (progress >= 100) {
                clearInterval(progressInterval);
            }
        }, 200);
    });
}

// Helper function to get translated text
function getTranslatedText(key) {
    const translations = {
        'en': {
            'unsupported_file_type': 'Unsupported file type. Please upload an image or video.',
            'processing_video': 'Processing video. This may take a few minutes...',
            'processing_complete': 'Processing Complete',
            'processed_frames': 'Processed Frames',
            'detections_found': 'Detections Found',
            'frame': 'Frame',
            'vehicle': 'Vehicle',
            'lane': 'Lane',
            'no_detections_found': 'No detections found in this video.',
            'processing_error': 'Error processing video',
            'license_plate_description': 'This mode detects and recognizes Chinese license plates in the image or video.',
            'lane_intrusion_description': 'This mode detects vehicles crossing lanes at intersections.'
        },
        'zh': {
            'unsupported_file_type': '不支持的文件类型。请上传图像或视频。',
            'processing_video': '正在处理视频。这可能需要几分钟...',
            'processing_complete': '处理完成',
            'processed_frames': '已处理帧数',
            'detections_found': '检测到的对象',
            'frame': '帧',
            'vehicle': '车辆',
            'lane': '车道',
            'no_detections_found': '在此视频中未发现检测结果。',
            'processing_error': '处理视频时出错',
            'license_plate_description': '此模式检测并识别图像或视频中的中国车牌。',
            'lane_intrusion_description': '此模式检测在十字路口穿越车道的车辆。'
        }
    };
    
    // Get current language
    const lang = document.documentElement.lang || 'zh';
    
    // Return the translated text
    return translations[lang][key] || key;
}
