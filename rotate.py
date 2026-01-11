import streamlit as st
from PIL import Image
from io import BytesIO
import os
import traceback
import time

st.set_page_config(layout="wide", page_title="Image 180° Rotator")

st.write("## Rotate your image 180°")
st.write("📸 Upload an image and it will be rotated 180 degrees automatically. Rotated images can be downloaded from the sidebar.")
st.sidebar.write("## Upload and download :gear:")

# Increased file size limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Max dimensions for processing
MAX_IMAGE_SIZE = 2000  # pixels

def convert_image(img: Image.Image) -> bytes:
    """Convert PIL image to PNG bytes for download."""
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def resize_image(image: Image.Image, max_size: int) -> Image.Image:
    """Resize image while maintaining aspect ratio."""
    width, height = image.size
    if width <= max_size and height <= max_size:
        return image

    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))

    return image.resize((new_width, new_height), Image.LANCZOS)

@st.cache_data
def process_image(image_bytes: bytes):
    """Process image with caching: resize (if needed) then rotate 180 degrees."""
    try:
        image = Image.open(BytesIO(image_bytes))

        # (Optional) Convert to RGBA to keep consistent output
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")

        resized = resize_image(image, MAX_IMAGE_SIZE)

        # 🔥 Rotate 180 degrees
        rotated = resized.rotate(180, expand=True)

        return image, rotated
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, None

def fix_image(upload):
    """Load image (uploaded or default path), rotate it, show results, and provide download."""
    try:
        start_time = time.time()
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()

        status_text.text("Loading image...")
        progress_bar.progress(10)

        # Read image bytes
        if isinstance(upload, str):
            # Default image path
            if not os.path.exists(upload):
                st.error(f"Default image not found at path: {upload}")
                return
            with open(upload, "rb") as f:
                image_bytes = f.read()
        else:
            # Uploaded file
            image_bytes = upload.getvalue()

        status_text.text("Processing image (rotate 180°)...")
        progress_bar.progress(30)

        # Process image (cached)
        image, rotated = process_image(image_bytes)
        if image is None or rotated is None:
            st.sidebar.error("Failed to process image.")
            return

        progress_bar.progress(80)
        status_text.text("Displaying results...")

        # Display images
        col1.write("Original Image :camera:")
        col1.image(image)

        col2.write("Rotated Image (180°) 🔄")
        col2.image(rotated)

        # Download button
        st.sidebar.markdown("\n")
        st.sidebar.download_button(
            "Download rotated image",
            convert_image(rotated),
            "rotated_180.png",
            "image/png"
        )

        progress_bar.progress(100)
        processing_time = time.time() - start_time
        status_text.text(f"Completed in {processing_time:.2f} seconds")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.sidebar.error("Failed to process image")
        print(f"Error in fix_image: {traceback.format_exc()}")

# UI Layout
col1, col2 = st.columns(2)
my_upload = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

# Information about limitations
with st.sidebar.expander("ℹ️ Image Guidelines"):
    st.write(f"""
    - Maximum file size: {MAX_FILE_SIZE/1024/1024:.1f}MB
    - Large images will be automatically resized (max dimension: {MAX_IMAGE_SIZE}px)
    - Supported formats: PNG, JPG, JPEG
    - Processing time depends on image size
    """)

# Process the image
if my_upload is not None:
    if my_upload.size > MAX_FILE_SIZE:
        st.error(f"The uploaded file is too large. Please upload an image smaller than {MAX_FILE_SIZE/1024/1024:.1f}MB.")
    else:
        fix_image(upload=my_upload)
else:
    # Try default images in order of preference
    default_images = ["./zebra.jpg", "./wallaby.png"]
    for img_path in default_images:
        if os.path.exists(img_path):
            fix_image(img_path)
            break
    else:
        st.info("Please upload an image to get started!")
