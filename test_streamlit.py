import streamlit as st
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import our custom modules
try:
    from i18n.translations import get_text, TRANSLATIONS
    translations_imported = True
except Exception as e:
    translations_imported = False
    translation_error = str(e)

# Set page config
st.set_page_config(
    page_title="Streamlit Test",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Main title
st.title("Streamlit Test Application")

# Display system information
st.header("System Information")
st.write(f"Python version: {sys.version}")
st.write(f"Current working directory: {os.getcwd()}")
st.write(f"Streamlit version: {st.__version__}")

# Test translations
st.header("Translations Test")
if translations_imported:
    st.success("✅ Translations module imported successfully")
    
    # Create language selector in sidebar
    with st.sidebar:
        st.header("Language / 语言")
        lang_options = {
            'zh': '中文',
            'en': 'English'
        }
        
        selected_lang = st.radio(
            label="Select Language",
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=0
        )
    
    # Display some sample translations
    st.subheader(f"Sample translations in {lang_options[selected_lang]}")
    st.write(f"Home: {get_text('home', selected_lang)}")
    st.write(f"License Plate Recognition: {get_text('license_plate_recognition', selected_lang)}")
    st.write(f"Upload Image or Video: {get_text('upload_image_video', selected_lang)}")
else:
    st.error(f"❌ Failed to import translations module: {translation_error}")

# Test file upload
st.header("File Upload Test")
uploaded_file = st.file_uploader("Upload a test image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
    st.image(uploaded_file, caption=f"Uploaded image: {uploaded_file.name}", use_column_width=True)

# Display a success message
st.balloons()
st.success("Streamlit test completed successfully!")
