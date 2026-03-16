import streamlit as st
from PIL import Image
import io
from processor import ImageProcessor

st.set_page_config(
    page_title="KnitImg Online",
    page_icon="🧶",
    layout="wide",
    initial_sidebar_state="collapsed", # Hide sidebar to prioritize 3-panel layout
)

# Premium Styling
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
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
    /* Fixed height for image previews to keep panels aligned */
    .stImage > img {
        max-height: 400px;
        object-fit: contain;
    }
    /* Panel headings */
    h3 {
        margin-bottom: 1rem !important;
        color: #31333F;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧶 KnitImg Online")
st.markdown("---")

# 3-Panel Layout
col_left, col_mid, col_right = st.columns([1, 1, 1], gap="large")

with col_left:
    st.write("### 🖼️ 1. Original")
    uploaded_file = st.file_uploader("Import Image", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
    else:
        st.info("Upload an image to start")

with col_mid:
    st.write("### ⚙️ 2. Functions")
    
    if uploaded_file is not None:
        # Rotate
        st.write("**Rotation**")
        rotate_enabled = st.checkbox("Enable Rotation", value=False, key="rot_en")
        rotate_angle = st.selectbox("Angle", ["90", "180", "270"], index=0, disabled=not rotate_enabled)
        
        st.divider()
        
        # Mirror
        st.write("**Mirroring**")
        mirror_enabled = st.checkbox("Enable Mirroring", value=False, key="mir_en")
        mirror_mode = st.selectbox("Mode", ["Left-Right", "Top-Bottom"], index=0, disabled=not mirror_enabled)
        
        st.divider()
        
        # Scale
        st.write("**Scaling**")
        scale_enabled = st.checkbox("Enable Scaling", value=True, key="scale_en")
        max_width = st.number_input("Max Width (px)", min_value=10, max_value=2000, value=200, step=10, disabled=not scale_enabled)
        stretch_enabled = st.checkbox("Compensate for non-rectangular stitches", value=False, disabled=not scale_enabled)
        stretch_factor = st.number_input("Vertical Stretch Factor", min_value=0.1, max_value=5.0, value=1.5, step=0.1, disabled=not (scale_enabled and stretch_enabled))
        
        st.divider()
        
        # Reduce Colors
        st.write("**Color Reduction**")
        reduce_enabled = st.checkbox("Enable Color Reduction", value=True, key="red_en")
        dither_mode = st.selectbox("Dithering Algorithm", 
                                  ["Floyd-Steinberg", "Atkinson", "Stucki", "Jarvis-Judice-Ninke", "Sierra", "Sierra Lite", "Ordered (Bayer 4x4)", "None"], 
                                  index=1, disabled=not reduce_enabled)
        
        st.write("Target Palette:")
        p_cols = st.columns(3)
        active_colors = []
        default_colors = ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00"]
        
        for i in range(6):
            with p_cols[i % 3]:
                is_active = st.checkbox(f"C{i+1}", value=(i < 2), key=f"c_en_{i}", disabled=not reduce_enabled)
                color = st.color_picker(f"C{i+1}", default_colors[i], key=f"c_val_{i}", label_visibility="collapsed", disabled=not reduce_enabled)
                if is_active:
                    rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    active_colors.append(rgb)
    else:
        st.warning("Please upload an image first")

with col_right:
    st.write("### ✨ 3. Result")
    
    if uploaded_file is not None:
        with st.spinner("Processing..."):
            processed_image = ImageProcessor.process(
                image,
                rotate_enabled=rotate_enabled,
                rotate_angle=rotate_angle,
                mirror_enabled=mirror_enabled,
                mirror_mode=mirror_mode,
                scale_enabled=scale_enabled,
                max_width=max_width,
                stretch_enabled=stretch_enabled,
                stretch_factor=stretch_factor,
                reduce_enabled=reduce_enabled,
                dither_mode=dither_mode,
                active_colors=active_colors if active_colors else None
            )
            
            st.image(processed_image, use_container_width=True)
            
            buf = io.BytesIO()
            processed_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📁 Download Result (PNG)",
                data=byte_im,
                file_name="knitimg_result.png",
                mime="image/png",
            )
    else:
        st.info("The processed image will appear here")

# Features Footer
st.markdown("---")
f1, f2, f3 = st.columns(3)
with f1:
    st.write("🚀 **Pro Dithering** - 8+ algorithms optimized for machines.")
with f2:
    st.write("📐 **Stitch Tuning** - Account for non-rectangular stitch shapes.")
with f3:
    st.write("🎨 **Exact Palettes** - Pick up to 6 colors matching your yarn.")
