// Main JavaScript functionality for the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupFileUpload();
    setupLanguageToggle();
    setupDetectionOptions();
    setupVideoProcessing();
    // Add navigation link to navbar
    addRealtimeNavLink();
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

// Add realtime detection link to navbar
function addRealtimeNavLink() {
    const navbarNav = document.getElementById('navbarNav');
    if (!navbarNav) return;

    const navList = navbarNav.querySelector('ul.navbar-nav');
    if (!navList) return;

    // Check if the link already exists
    if (navList.querySelector('a[href="/realtime"]')) return;

    // Create new list item
    const listItem = document.createElement('li');
    listItem.className = 'nav-item';

    // Create link
    const link = document.createElement('a');
    link.className = 'nav-link';
    link.href = '/realtime';

    // Add icon and text
    const icon = document.createElement('i');
    icon.className = 'fas fa-video me-1';
    link.appendChild(icon);

    // Add text based on language
    const lang = document.documentElement.lang || 'zh';
    const text = document.createTextNode(lang === 'zh' ? '实时检测' : 'Real-time Detection');
    link.appendChild(text);

    // Add link to list item
    listItem.appendChild(link);

    // Add list item to navbar before the language toggle
    const langToggleItem = navList.querySelector('form#languageForm').closest('li');
    navList.insertBefore(listItem, langToggleItem);
}

// Initialize realtime detection
function initRealtimeDetection() {
    // Elements
    const startCameraBtn = document.getElementById('startCameraBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    const captureBtn = document.getElementById('captureBtn');
    const cameraSelect = document.getElementById('cameraSelect');
    const cameraFeed = document.getElementById('cameraFeed');
    const processingCanvas = document.getElementById('processingCanvas');
    const cameraPlaceholder = document.getElementById('cameraPlaceholder');
    const liveResults = document.getElementById('liveResults');
    const recentCaptures = document.getElementById('recentCaptures');
    const processingInterval = document.getElementById('processingInterval');
    const intervalValue = document.getElementById('intervalValue');
    const autoSaveSwitch = document.getElementById('autoSaveSwitch');
    const showBoundingBoxesSwitch = document.getElementById('showBoundingBoxesSwitch');
    const realtimeDetectionOptions = document.querySelectorAll('input[name="realtime_detection_type"]');

    // If elements don't exist, we're not on the realtime page
    if (!startCameraBtn || !cameraFeed) return;

    // Variables
    let stream = null;
    let processingIntervalId = null;
    let currentDetectionType = 'license_plate';
    let captureCount = 0;

    // Update interval display
    processingInterval.addEventListener('input', function() {
        intervalValue.textContent = this.value + ' ms';

        // If processing is active, restart with new interval
        if (processingIntervalId) {
            clearInterval(processingIntervalId);
            startProcessing();
        }
    });

    // Update detection type
    realtimeDetectionOptions.forEach(option => {
        option.addEventListener('change', function() {
            currentDetectionType = this.value;

            // Clear results
            liveResults.innerHTML = '<div class="text-center p-3"><div class="spinner-border text-primary"></div><p class="mt-2">' +
                                   getTranslatedText('switching_detection_mode') + '</p></div>';
        });
    });

    // Enumerate cameras
    async function getCameras() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(device => device.kind === 'videoinput');

            // Clear select options
            cameraSelect.innerHTML = '';

            // Add default option
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = getTranslatedText('default_camera');
            cameraSelect.appendChild(defaultOption);

            // Add each camera
            videoDevices.forEach((device, index) => {
                const option = document.createElement('option');
                option.value = device.deviceId;
                option.textContent = device.label || `Camera ${index + 1}`;
                cameraSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error enumerating cameras:', error);
        }
    }

    // Start camera
    async function startCamera() {
        try {
            const constraints = {
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };

            // Use selected camera if specified
            if (cameraSelect.value) {
                constraints.video.deviceId = { exact: cameraSelect.value };
            }

            // Get user media
            stream = await navigator.mediaDevices.getUserMedia(constraints);

            // Show video element
            cameraFeed.srcObject = stream;
            cameraFeed.style.display = 'block';
            processingCanvas.style.display = 'block';
            cameraPlaceholder.style.display = 'none';

            // Enable/disable buttons
            startCameraBtn.disabled = true;
            stopCameraBtn.disabled = false;
            captureBtn.disabled = false;

            // Start processing
            startProcessing();

            // Update camera list with labels (requires permission)
            getCameras();
        } catch (error) {
            console.error('Error starting camera:', error);
            liveResults.innerHTML = `<div class="alert alert-danger">${getTranslatedText('camera_error')}: ${error.message}</div>`;
        }
    }

    // Stop camera
    function stopCamera() {
        if (stream) {
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
            stream = null;

            // Hide video element
            cameraFeed.srcObject = null;
            cameraFeed.style.display = 'none';
            processingCanvas.style.display = 'none';
            cameraPlaceholder.style.display = 'block';

            // Enable/disable buttons
            startCameraBtn.disabled = false;
            stopCameraBtn.disabled = true;
            captureBtn.disabled = true;

            // Stop processing
            if (processingIntervalId) {
                clearInterval(processingIntervalId);
                processingIntervalId = null;
            }
        }
    }

    // Start processing frames
    function startProcessing() {
        if (processingIntervalId) {
            clearInterval(processingIntervalId);
        }

        processingIntervalId = setInterval(processFrame, parseInt(processingInterval.value));
    }

    // Process current frame
    function processFrame() {
        if (!stream) return;

        // Draw current frame to canvas
        const context = processingCanvas.getContext('2d');
        processingCanvas.width = cameraFeed.videoWidth;
        processingCanvas.height = cameraFeed.videoHeight;
        context.drawImage(cameraFeed, 0, 0, processingCanvas.width, processingCanvas.height);

        // Get image data
        const imageData = processingCanvas.toDataURL('image/jpeg');

        // Send to server for processing
        const formData = new FormData();
        formData.append('image_data', imageData);
        formData.append('detection_type', currentDetectionType);
        formData.append('show_boxes', showBoundingBoxesSwitch.checked);

        fetch('/process_realtime', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Processing error:', data.error);
                return;
            }

            // Update canvas with processed image
            if (data.processed_image) {
                const img = new Image();
                img.onload = function() {
                    context.drawImage(img, 0, 0, processingCanvas.width, processingCanvas.height);
                };
                img.src = 'data:image/jpeg;base64,' + data.processed_image;
            }

            // Update results
            updateLiveResults(data);

            // Auto-save if enabled and detections found
            if (autoSaveSwitch.checked && hasDetections(data)) {
                captureCurrentFrame(data);
            }
        })
        .catch(error => {
            console.error('Error processing frame:', error);
        });
    }

    // Check if data has detections
    function hasDetections(data) {
        if (currentDetectionType === 'license_plate') {
            return data.detections && data.detections.some(d => d.license_plate);
        } else {
            return data.intrusions && data.intrusions.length > 0;
        }
    }

    // Update live results display
    function updateLiveResults(data) {
        // Clear previous results
        liveResults.innerHTML = '';

        if (currentDetectionType === 'license_plate' && data.detections) {
            // Filter detections with license plates
            const plateDetections = data.detections.filter(d => d.license_plate);

            if (plateDetections.length > 0) {
                // Create header
                const header = document.createElement('h6');
                header.className = 'mb-3';
                header.textContent = getTranslatedText('detected_license_plates');
                liveResults.appendChild(header);

                // Add each plate
                plateDetections.forEach(detection => {
                    const plateDiv = document.createElement('div');
                    plateDiv.className = 'license-plate mb-2';
                    plateDiv.textContent = detection.license_plate;

                    const confidenceDiv = document.createElement('div');
                    confidenceDiv.className = 'small text-muted mb-3';
                    confidenceDiv.textContent = `${getTranslatedText('confidence')}: ${(detection.confidence * 100).toFixed(1)}%`;

                    liveResults.appendChild(plateDiv);
                    liveResults.appendChild(confidenceDiv);
                });
            } else {
                // No plates detected
                const noDetections = document.createElement('div');
                noDetections.className = 'alert alert-info';
                noDetections.textContent = getTranslatedText('no_plates_detected');
                liveResults.appendChild(noDetections);
            }
        } else if (currentDetectionType === 'lane_intrusion' && data.intrusions) {
            if (data.intrusions.length > 0) {
                // Create header
                const header = document.createElement('h6');
                header.className = 'mb-3';
                header.textContent = getTranslatedText('detected_intrusions');
                liveResults.appendChild(header);

                // Add each intrusion
                data.intrusions.forEach(intrusion => {
                    const intrusionDiv = document.createElement('div');
                    intrusionDiv.className = 'alert alert-danger mb-2 py-2';
                    intrusionDiv.textContent = `${getTranslatedText('vehicle')} ${intrusion.vehicle_id}: ${getTranslatedText('lane')} ${intrusion.from_lane + 1} → ${intrusion.to_lane + 1}`;
                    liveResults.appendChild(intrusionDiv);
                });
            } else {
                // No intrusions detected
                const noIntrusions = document.createElement('div');
                noIntrusions.className = 'alert alert-success';
                noIntrusions.textContent = getTranslatedText('no_intrusions_detected');
                liveResults.appendChild(noIntrusions);
            }
        }
    }

    // Capture current frame
    function captureCurrentFrame(data = null) {
        if (!stream) return;

        // Increment capture count
        captureCount++;

        // Get canvas data
        const imageData = processingCanvas.toDataURL('image/jpeg');

        // Create form data
        const formData = new FormData();
        formData.append('image_data', imageData);
        formData.append('detection_type', currentDetectionType);
        formData.append('capture_id', captureCount);

        // If we have detection data, include it
        if (data) {
            formData.append('detection_data', JSON.stringify(data));
        }

        // Send to server
        fetch('/save_capture', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error saving capture:', data.error);
                return;
            }

            // Add to recent captures
            addCaptureToGallery(data.image_path, data.detection_id);
        })
        .catch(error => {
            console.error('Error saving capture:', error);
        });
    }

    // Add capture to gallery
    function addCaptureToGallery(imagePath, detectionId) {
        // Clear placeholder if present
        if (recentCaptures.querySelector('div.text-muted')) {
            recentCaptures.innerHTML = '';
        }

        // Create column
        const col = document.createElement('div');
        col.className = 'col-md-3 col-sm-6 mb-3';

        // Create card
        const card = document.createElement('div');
        card.className = 'card h-100';

        // Create card body
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body p-2';

        // Create image
        const img = document.createElement('img');
        img.className = 'img-fluid rounded mb-2';
        img.src = imagePath;
        img.alt = 'Capture ' + captureCount;

        // Create link to view detection
        const link = document.createElement('a');
        link.className = 'btn btn-sm btn-primary d-block';
        link.href = '/view_detection/' + detectionId;

        // Add icon and text
        const icon = document.createElement('i');
        icon.className = 'fas fa-eye me-1';
        link.appendChild(icon);

        const text = document.createTextNode(getTranslatedText('view_details'));
        link.appendChild(text);

        // Assemble card
        cardBody.appendChild(img);
        cardBody.appendChild(link);
        card.appendChild(cardBody);
        col.appendChild(card);

        // Add to gallery (at the beginning)
        if (recentCaptures.firstChild) {
            recentCaptures.insertBefore(col, recentCaptures.firstChild);
        } else {
            recentCaptures.appendChild(col);
        }

        // Limit to 8 recent captures
        const captures = recentCaptures.querySelectorAll('.col-md-3');
        if (captures.length > 8) {
            recentCaptures.removeChild(captures[captures.length - 1]);
        }
    }

    // Event listeners
    startCameraBtn.addEventListener('click', startCamera);
    stopCameraBtn.addEventListener('click', stopCamera);
    captureBtn.addEventListener('click', () => captureCurrentFrame());

    // Initialize camera selection
    getCameras();
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
            'lane_intrusion_description': 'This mode detects vehicles crossing lanes at intersections.',
            'default_camera': 'Default Camera',
            'camera_error': 'Camera error',
            'detected_license_plates': 'Detected License Plates',
            'detected_intrusions': 'Detected Intrusions',
            'no_plates_detected': 'No license plates detected',
            'no_intrusions_detected': 'No lane intrusions detected',
            'confidence': 'Confidence',
            'view_details': 'View Details',
            'switching_detection_mode': 'Switching detection mode...'
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
            'lane_intrusion_description': '此模式检测在十字路口穿越车道的车辆。',
            'default_camera': '默认相机',
            'camera_error': '相机错误',
            'detected_license_plates': '检测到的车牌',
            'detected_intrusions': '检测到的车道入侵',
            'no_plates_detected': '未检测到车牌',
            'no_intrusions_detected': '未检测到车道入侵',
            'confidence': '置信度',
            'view_details': '查看详情',
            'switching_detection_mode': '切换检测模式...'
        }
    };

    // Get current language
    const lang = document.documentElement.lang || 'zh';

    // Return the translated text
    return translations[lang][key] || key;
}
