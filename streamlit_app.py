import streamlit as st
from PIL import Image
import io
from processor import ImageProcessor

st.set_page_config(
    page_title="KnitImg Online",
    page_icon="🧶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium Styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
    .stDownloadButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #28a745;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧶 KnitImg Online")
st.subheader("Machine Knitting Image Assistant")

# Sidebar for Controls
st.sidebar.header("Processing Controls")

uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    original_image = image.copy()
    
    with st.sidebar:
        # 1. Rotate
        st.write("### 1. Rotation")
        rotate_enabled = st.checkbox("Enable Rotation", value=False)
        rotate_angle = st.selectbox("Angle", ["90", "180", "270"], index=0, disabled=not rotate_enabled)
        
        st.divider()
        
        # 2. Mirror
        st.write("### 2. Mirroring")
        mirror_enabled = st.checkbox("Enable Mirroring", value=False)
        mirror_mode = st.selectbox("Mode", ["Left-Right", "Top-Bottom"], index=0, disabled=not mirror_enabled)
        
        st.divider()
        
        # 3. Scale
        st.write("### 3. Scaling")
        scale_enabled = st.checkbox("Enable Scaling", value=True)
        max_width = st.number_input("Max Width (px)", min_value=10, max_value=2000, value=200, step=10, disabled=not scale_enabled)
        shrink_enabled = st.checkbox("Account for Rectangular Stitches", value=False, disabled=not scale_enabled)
        shrink_factor = st.number_input("Vertical Shrink Factor", min_value=0.1, max_value=5.0, value=1.5, step=0.1, disabled=not (scale_enabled and shrink_enabled))
        
        st.divider()
        
        # 4. Reduce Colors
        st.write("### 4. Color Reduction")
        reduce_enabled = st.checkbox("Enable Color Reduction", value=True)
        dither_mode = st.selectbox("Dithering Algorithm", 
                                  ["Floyd-Steinberg", "Atkinson", "Stucki", "Jarvis-Judice-Ninke", "Sierra", "Sierra Lite", "Ordered (Bayer 4x4)", "None"], 
                                  index=1, disabled=not reduce_enabled)
        
        st.write("Select Palette (Max 6):")
        cols = st.columns(3)
        active_colors = []
        default_colors = [
            "#000000", "#FFFFFF", "#FF0000", 
            "#00FF00", "#0000FF", "#FFFF00"
        ]
        
        for i in range(6):
            with cols[i % 3]:
                is_active = st.checkbox(f"C{i+1}", value=(i < 2), key=f"c_en_{i}", disabled=not reduce_enabled)
                color = st.color_picker(f"Pick C{i+1}", default_colors[i], key=f"c_val_{i}", label_visibility="collapsed", disabled=not reduce_enabled)
                if is_active:
                    # Convert hex to RGB tuple
                    rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    active_colors.append(rgb)

    # Main Area Layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Original")
        st.image(original_image, use_container_width=True)
        
    with col2:
        st.write("### Result")
        
        # Process image
        with st.spinner("Processing..."):
            processed_image = ImageProcessor.process(
                original_image,
                rotate_enabled=rotate_enabled,
                rotate_angle=rotate_angle,
                mirror_enabled=mirror_enabled,
                mirror_mode=mirror_mode,
                scale_enabled=scale_enabled,
                max_width=max_width,
                shrink_enabled=shrink_enabled,
                shrink_factor=shrink_factor,
                reduce_enabled=reduce_enabled,
                dither_mode=dither_mode,
                active_colors=active_colors if active_colors else None
            )
            
            st.image(processed_image, use_container_width=True)
            
            # Export to buffer
            buf = io.BytesIO()
            processed_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="Download Result (PNG)",
                data=byte_im,
                file_name="knitimg_result.png",
                mime="image/png",
            )
else:
    st.info("Upload an image in the sidebar to get started! 🧶")
    
    # Feature Showcase
    st.write("---")
    st.write("### ✨ Features")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("🚀 **Fast Dithering**")
        st.write("Optimized 8+ algorithms including Atkinson and Floyd-Steinberg.")
    with c2:
        st.write("📐 **Stitch Scaling**")
        st.write("Adjust vertical factor to account for rectangular knitting stitches.")
    with c3:
        st.write("🎨 **Custom Palettes**")
        st.write("Pick up to 6 exact colors to match your yarn stock.")
