import streamlit as st

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Lane Intrusion Detection System",  # Default title before language is set
    page_icon="🚗",
    layout="wide"
)

import os
import cv2
import numpy as np
import time
from PIL import Image
import io
import base64
import logging
from typing import Tuple, List, Dict, Any, Optional

# Import custom modules
from detection.yolo_detector import YOLODetector
from detection.license_plate_recognition import LicensePlateRecognizer
from detection.lane_intrusion import LaneIntrusionDetector
from utils.helpers import process_image
from i18n.translations import get_text, TRANSLATIONS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize detectors
@st.cache_resource
def load_models():
    yolo_detector = YOLODetector()
    license_plate_recognizer = LicensePlateRecognizer()
    lane_intrusion_detector = LaneIntrusionDetector()
    return yolo_detector, license_plate_recognizer, lane_intrusion_detector

# Create temporary directory for uploads if it doesn't exist
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_uploaded_file(upload_file) -> str:
    """Save uploaded file to temp directory and return the file path"""
    file_path = os.path.join(UPLOAD_DIR, upload_file.name)
    with open(file_path, "wb") as f:
        f.write(upload_file.getbuffer())
    return file_path

def get_binary_file_downloader_html(bin_file, file_label='File'):
    """Generate HTML code for file download link"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

def main():
    
    # Load models
    yolo_detector, license_plate_recognizer, lane_intrusion_detector = load_models()
    
    # Session state initialization
    if 'language' not in st.session_state:
        st.session_state['language'] = 'zh'
    
    # Create language selector in sidebar
    with st.sidebar:
        lang_options = {
            'zh': '中文',
            'en': 'English'
        }
        
        selected_lang = st.radio(
            label="Language / 语言",
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=0 if st.session_state['language'] == 'zh' else 1
        )
        
        if selected_lang != st.session_state['language']:
            st.session_state['language'] = selected_lang
            st.experimental_rerun()
    
    # Get current language
    lang = st.session_state['language']
    
    # Main title
    st.title(get_text('app_title', lang))
    
    # Description
    st.markdown(get_text('app_description', lang))
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs([
        get_text('license_plate_tab', lang),
        get_text('lane_intrusion_tab', lang)
    ])
    
    # License Plate Recognition Tab
    with tab1:
        st.header(get_text('license_plate_recognition', lang))
        st.markdown(get_text('license_plate_description', lang))
        
        # File uploader for license plate detection
        license_plate_file = st.file_uploader(
            get_text('upload_image_video', lang),
            type=['jpg', 'jpeg', 'png', 'mp4', 'avi'],
            key="license_plate_uploader"
        )
        
        if license_plate_file is not None:
            # Save uploaded file
            file_path = save_uploaded_file(license_plate_file)
            
            # Check if video or image
            is_video = file_path.lower().endswith(('.mp4', '.avi'))
            
            if is_video:
                st.video(file_path)
                
                if st.button(get_text('process_video', lang), key="process_lp_video"):
                    # Process video frame by frame
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    cap = cv2.VideoCapture(file_path)
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    
                    # Initialize result containers
                    all_results = []
                    processed_frames = 0
                    detected_plates = 0
                    
                    # Create columns for results
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        result_placeholder = st.empty()
                    
                    with col2:
                        details_placeholder = st.empty()
                    
                    start_time = time.time()
                    
                    # Process every 10th frame to reduce computational load
                    frame_interval = 10
                    
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        processed_frames += 1
                        
                        # Update progress
                        progress = processed_frames / total_frames
                        progress_bar.progress(progress)
                        status_text.text(f"{get_text('processing_frame', lang)} {processed_frames}/{total_frames}")
                        
                        # Only process every n-th frame
                        if processed_frames % frame_interval != 0:
                            continue
                        
                        # Save frame temporarily
                        temp_frame_path = os.path.join(UPLOAD_DIR, f"temp_frame_{processed_frames}.jpg")
                        cv2.imwrite(temp_frame_path, frame)
                        
                        # Process frame
                        result, output_image = process_image(
                            temp_frame_path, 
                            'license_plate', 
                            yolo_detector, 
                            license_plate_recognizer, 
                            lane_intrusion_detector
                        )
                        
                        # Show the latest processed frame
                        result_placeholder.image(
                            output_image, 
                            caption=f"{get_text('frame', lang)} {processed_frames}", 
                            use_column_width=True,
                            channels="BGR"
                        )
                        
                        # Count detected plates
                        if 'detections' in result:
                            for detection in result['detections']:
                                if 'license_plate' in detection and detection['license_plate']:
                                    detected_plates += 1
                        
                        # Add frame info to results
                        result['frame'] = processed_frames
                        all_results.append(result)
                        
                        # Display current stats
                        details_placeholder.write(f"""
                        ### {get_text('processing_stats', lang)}
                        - {get_text('elapsed_time', lang)}: {time.time() - start_time:.2f}s
                        - {get_text('processed_frames', lang)}: {processed_frames}/{total_frames}
                        - {get_text('detected_plates', lang)}: {detected_plates}
                        """)
                        
                        # Clean up temp frame file
                        os.remove(temp_frame_path)
                    
                    cap.release()
                    
                    # Final stats and results
                    st.success(get_text('video_processing_complete', lang))
                    
                    st.write(f"### {get_text('processing_results', lang)}")
                    st.write(f"- {get_text('total_frames', lang)}: {total_frames}")
                    st.write(f"- {get_text('processed_frames', lang)}: {processed_frames}")
                    st.write(f"- {get_text('detected_plates', lang)}: {detected_plates}")
                    st.write(f"- {get_text('processing_time', lang)}: {time.time() - start_time:.2f}s")
                    
                    # Show detections in an expander
                    with st.expander(get_text('view_all_detections', lang)):
                        for result in all_results:
                            if 'detections' in result and result['detections']:
                                st.write(f"#### {get_text('frame', lang)} {result['frame']}")
                                
                                for detection in result['detections']:
                                    if 'license_plate' in detection and detection['license_plate']:
                                        st.code(detection['license_plate'], language="plain")
                                        st.write(f"{get_text('confidence', lang)}: {detection['confidence']:.2f}")
                                
                                st.markdown("---")
            else:
                # Process image
                st.image(file_path, caption=get_text('uploaded_image', lang), use_column_width=True)
                
                if st.button(get_text('process_image', lang), key="process_lp_image"):
                    with st.spinner(get_text('processing', lang)):
                        # Process the image
                        result, output_image = process_image(
                            file_path, 
                            'license_plate', 
                            yolo_detector, 
                            license_plate_recognizer, 
                            lane_intrusion_detector
                        )
                        
                        # Create columns for results
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.image(
                                output_image, 
                                caption=get_text('processed_image', lang), 
                                use_column_width=True,
                                channels="BGR"
                            )
                            
                            # Save and offer download
                            output_path = os.path.join(UPLOAD_DIR, "processed_" + os.path.basename(file_path))
                            cv2.imwrite(output_path, output_image)
                            st.markdown(
                                get_binary_file_downloader_html(
                                    output_path, 
                                    get_text('download_result', lang)
                                ), 
                                unsafe_allow_html=True
                            )
                        
                        with col2:
                            st.subheader(get_text('detection_results', lang))
                            
                            if 'detections' in result and result['detections']:
                                for i, detection in enumerate(result['detections']):
                                    if 'license_plate' in detection and detection['license_plate']:
                                        st.write(f"#### {get_text('plate', lang)} {i+1}")
                                        
                                        # Display license plate in a styled box
                                        st.markdown(
                                            f"""
                                            <div style="
                                                background-color: white; 
                                                color: black; 
                                                padding: 10px; 
                                                border: 2px solid black; 
                                                border-radius: 5px; 
                                                display: inline-block; 
                                                font-family: monospace; 
                                                font-size: 18px; 
                                                font-weight: bold;
                                                margin: 5px 0 15px 0;
                                            ">
                                                {detection['license_plate']}
                                            </div>
                                            """, 
                                            unsafe_allow_html=True
                                        )
                                        
                                        st.write(f"{get_text('confidence', lang)}: {detection['confidence']:.2f}")
                                        st.markdown("---")
                            else:
                                st.warning(get_text('no_plates_found', lang))
    
    # Lane Intrusion Detection Tab
    with tab2:
        st.header(get_text('lane_intrusion_detection', lang))
        st.markdown(get_text('lane_intrusion_description', lang))
        
        # File uploader for lane intrusion detection
        lane_intrusion_file = st.file_uploader(
            get_text('upload_image_video', lang),
            type=['jpg', 'jpeg', 'png', 'mp4', 'avi'],
            key="lane_intrusion_uploader"
        )
        
        if lane_intrusion_file is not None:
            # Save uploaded file
            file_path = save_uploaded_file(lane_intrusion_file)
            
            # Check if video or image
            is_video = file_path.lower().endswith(('.mp4', '.avi'))
            
            if is_video:
                st.video(file_path)
                
                if st.button(get_text('process_video', lang), key="process_li_video"):
                    # Process video frame by frame
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    cap = cv2.VideoCapture(file_path)
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    
                    # Initialize result containers
                    all_results = []
                    processed_frames = 0
                    intrusion_events = 0
                    
                    # Create columns for results
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        result_placeholder = st.empty()
                    
                    with col2:
                        details_placeholder = st.empty()
                    
                    start_time = time.time()
                    
                    # Process every 5th frame
                    frame_interval = 5
                    
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        processed_frames += 1
                        
                        # Update progress
                        progress = processed_frames / total_frames
                        progress_bar.progress(progress)
                        status_text.text(f"{get_text('processing_frame', lang)} {processed_frames}/{total_frames}")
                        
                        # Only process every n-th frame
                        if processed_frames % frame_interval != 0:
                            continue
                        
                        # Save frame temporarily
                        temp_frame_path = os.path.join(UPLOAD_DIR, f"temp_frame_{processed_frames}.jpg")
                        cv2.imwrite(temp_frame_path, frame)
                        
                        # Process frame
                        result, output_image = process_image(
                            temp_frame_path, 
                            'lane_intrusion', 
                            yolo_detector, 
                            license_plate_recognizer, 
                            lane_intrusion_detector
                        )
                        
                        # Show the latest processed frame
                        result_placeholder.image(
                            output_image, 
                            caption=f"{get_text('frame', lang)} {processed_frames}", 
                            use_column_width=True,
                            channels="BGR"
                        )
                        
                        # Count intrusion events
                        if 'intrusions' in result:
                            intrusion_events += len(result['intrusions'])
                        
                        # Add frame info to results
                        result['frame'] = processed_frames
                        all_results.append(result)
                        
                        # Display current stats
                        details_placeholder.write(f"""
                        ### {get_text('processing_stats', lang)}
                        - {get_text('elapsed_time', lang)}: {time.time() - start_time:.2f}s
                        - {get_text('processed_frames', lang)}: {processed_frames}/{total_frames}
                        - {get_text('intrusion_events', lang)}: {intrusion_events}
                        """)
                        
                        # Clean up temp frame file
                        os.remove(temp_frame_path)
                    
                    cap.release()
                    
                    # Final stats and results
                    st.success(get_text('video_processing_complete', lang))
                    
                    st.write(f"### {get_text('processing_results', lang)}")
                    st.write(f"- {get_text('total_frames', lang)}: {total_frames}")
                    st.write(f"- {get_text('processed_frames', lang)}: {processed_frames}")
                    st.write(f"- {get_text('intrusion_events', lang)}: {intrusion_events}")
                    st.write(f"- {get_text('processing_time', lang)}: {time.time() - start_time:.2f}s")
                    
                    # Show intrusions in an expander
                    with st.expander(get_text('view_all_intrusions', lang)):
                        for result in all_results:
                            if 'intrusions' in result and result['intrusions']:
                                st.write(f"#### {get_text('frame', lang)} {result['frame']}")
                                
                                for intrusion in result['intrusions']:
                                    st.warning(
                                        f"{get_text('vehicle', lang)} #{intrusion['vehicle_id']}: "
                                        f"{get_text('lane', lang)} {intrusion['from_lane']+1} → "
                                        f"{get_text('lane', lang)} {intrusion['to_lane']+1}"
                                    )
                                
                                st.markdown("---")
            else:
                # Process image
                st.image(file_path, caption=get_text('uploaded_image', lang), use_column_width=True)
                
                if st.button(get_text('process_image', lang), key="process_li_image"):
                    with st.spinner(get_text('processing', lang)):
                        # Process the image
                        result, output_image = process_image(
                            file_path, 
                            'lane_intrusion', 
                            yolo_detector, 
                            license_plate_recognizer, 
                            lane_intrusion_detector
                        )
                        
                        # Create columns for results
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.image(
                                output_image, 
                                caption=get_text('processed_image', lang), 
                                use_column_width=True,
                                channels="BGR"
                            )
                            
                            # Save and offer download
                            output_path = os.path.join(UPLOAD_DIR, "processed_" + os.path.basename(file_path))
                            cv2.imwrite(output_path, output_image)
                            st.markdown(
                                get_binary_file_downloader_html(
                                    output_path, 
                                    get_text('download_result', lang)
                                ), 
                                unsafe_allow_html=True
                            )
                        
                        with col2:
                            st.subheader(get_text('detection_results', lang))
                            
                            # Display vehicle info
                            if 'vehicles' in result and result['vehicles']:
                                st.write(f"##### {get_text('vehicles_detected', lang)}: {len(result['vehicles'])}")
                                
                                # Show vehicle lanes
                                vehicle_lanes = {}
                                for vehicle in result['vehicles']:
                                    lane = vehicle.get('lane', -1)
                                    if lane not in vehicle_lanes:
                                        vehicle_lanes[lane] = 0
                                    vehicle_lanes[lane] += 1
                                
                                for lane, count in vehicle_lanes.items():
                                    if lane == -1:
                                        lane_text = get_text('no_lane', lang)
                                    else:
                                        lane_text = f"{get_text('lane', lang)} {lane+1}"
                                    
                                    st.write(f"- {lane_text}: {count} {get_text('vehicles', lang)}")
                            
                            # Display intrusion events
                            if 'intrusions' in result and result['intrusions']:
                                st.markdown("---")
                                st.write(f"##### {get_text('intrusion_events', lang)}: {len(result['intrusions'])}")
                                
                                for intrusion in result['intrusions']:
                                    st.warning(
                                        f"{get_text('vehicle', lang)} #{intrusion['vehicle_id']}: "
                                        f"{get_text('lane', lang)} {intrusion['from_lane']+1} → "
                                        f"{get_text('lane', lang)} {intrusion['to_lane']+1}"
                                    )
                            else:
                                st.markdown("---")
                                st.success(get_text('no_intrusions_detected', lang))

if __name__ == "__main__":
    main()
