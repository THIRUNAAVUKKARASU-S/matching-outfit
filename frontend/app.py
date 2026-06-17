import os
import requests
import io
import streamlit as tf
from PIL import Image

# Using a standard import name 'st' inside Streamlit apps for idiomatic consistency,
# but using 'st' as the alias.
import streamlit as st

# Configure page metadata
st.set_page_config(
    page_title="AI TryOn & Outfit Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS styling for a state-of-the-art dark-mode aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;600&display=swap');

    /* General background and fonts */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, .title-text {
        font-family: 'Outfit', sans-serif;
    }

    /* Gradient Banner */
    .gradient-banner {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px -5px rgba(124, 58, 237, 0.4);
    }
    .gradient-banner h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.05em;
    }
    .gradient-banner p {
        font-size: 1.1rem;
        font-weight: 300;
        opacity: 0.95;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B0F19;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        color: #818CF8;
    }

    /* Style the main Generate Button */
    div.stButton > button {
        background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%);
        color: #FFFFFF !important;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35);
        width: 100%;
        margin-top: 1rem;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5);
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        border: none;
    }
    div.stButton > button:active {
        transform: translateY(1px);
    }

    /* Container blocks */
    .image-container {
        background-color: #1E293B;
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #334155;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .container-title {
        font-weight: 600;
        color: #94A3B8;
        margin-bottom: 0.8rem;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Accessory Grid Cards (Glassmorphism) */
    .accessory-grid {
        display: flex;
        gap: 1.5rem;
        margin-top: 1.5rem;
        flex-wrap: wrap;
    }
    .accessory-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.2rem;
        flex: 1;
        min-width: 250px;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .accessory-card:hover {
        transform: translateY(-8px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.2);
    }
    .accessory-img-container {
        width: 100%;
        border-radius: 10px;
        overflow: hidden;
        background-color: #F8FAFC;
        margin-bottom: 0.8rem;
        height: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .accessory-img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }
    .accessory-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 1.15rem;
        color: #F8FAFC;
        margin-bottom: 0.3rem;
    }
    .accessory-price {
        font-family: 'Outfit', sans-serif;
        color: #38BDF8;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 0.4rem;
    }
    .accessory-desc {
        font-size: 0.85rem;
        color: #94A3B8;
        line-height: 1.4;
        margin-bottom: 0.8rem;
    }
    .badge {
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        width: fit-content;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-formal {
        background-color: rgba(139, 92, 246, 0.15);
        color: #C084FC;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }
    .badge-sporty {
        background-color: rgba(20, 184, 166, 0.15);
        color: #2DD4BF;
        border: 1px solid rgba(20, 184, 166, 0.3);
    }
    .badge-casual {
        background-color: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    /* Badges for Try-On source */
    .ai-badge {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.2);
    }
    .fallback-badge {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        box-shadow: 0 4px 10px rgba(245, 158, 11, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Main Banner Layout
st.markdown("""
<div class="gradient-banner">
    <h1>✨ AI TryOn & Outfit Studio</h1>
    <p>Realistic Virtual Fitting Room & Outfit Matching Recommendation Assistant</p>
</div>
""", unsafe_allow_html=True)

# Server connection configurations
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Setup Sidebar Configurations
st.sidebar.markdown("## ⚙️ Control Center")

use_demo = st.sidebar.checkbox("🎁 Use Demo Model & Garment", value=False, help="Loads a default model and a summer dress to quickly test the try-on without uploading files.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏷️ Garment Metadata")
garment_desc = st.sidebar.text_input(
    "Garment Description", 
    value="Premium Floral Print Summer Dress",
    help="Brief text describing the style and colors. Feeds into recommendation engine."
)
category = st.sidebar.selectbox(
    "Garment Category", 
    ["upper_body", "lower_body", "dresses"],
    index=2,
    help="Target category mapping for the try-on placement."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧬 AI Advanced Options")
denoise_steps = st.sidebar.slider("Denoising Steps", min_value=10, max_value=50, value=30, help="Number of diffusion iterations. Higher values yield finer quality but take longer.")
seed = st.sidebar.number_input("Inference Seed", value=42, step=1, help="Fixes randomness to yield reproducible overlays.")

# Setup visual columns for image upload
col1, col2 = st.columns(2)

person_bytes = None
garment_bytes = None

with col1:
    st.markdown('<div class="image-container"><div class="container-title">👤 Target Person</div>', unsafe_allow_html=True)
    if use_demo:
        demo_person_path = "data/samples/person.png"
        if os.path.exists(demo_person_path):
            st.image(demo_person_path, use_container_width=True)
            with open(demo_person_path, "rb") as f:
                person_bytes = f.read()
        else:
            st.error("Demo person file missing. Please uncheck demo mode.")
    else:
        uploaded_person = st.file_uploader("Upload Person Photo (Full/Half Body)", type=["jpg", "jpeg", "png"], key="person_uploader")
        if uploaded_person:
            st.image(uploaded_person, use_container_width=True)
            person_bytes = uploaded_person.getvalue()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="image-container"><div class="container-title">👕 Garment Item</div>', unsafe_allow_html=True)
    if use_demo:
        demo_garment_path = "data/samples/garment.png"
        if os.path.exists(demo_garment_path):
            st.image(demo_garment_path, use_container_width=True)
            with open(demo_garment_path, "rb") as f:
                garment_bytes = f.read()
        else:
            st.error("Demo garment file missing. Please uncheck demo mode.")
    else:
        uploaded_garment = st.file_uploader("Upload Garment Flat-Lay/Model Photo", type=["jpg", "jpeg", "png"], key="garment_uploader")
        if uploaded_garment:
            st.image(uploaded_garment, use_container_width=True)
            garment_bytes = uploaded_garment.getvalue()
    st.markdown('</div>', unsafe_allow_html=True)

# Generate Try-On Button Action
trigger_generate = st.button("✨ Generate Try-On Model Overlay & Accessories")

if trigger_generate:
    if person_bytes is None or garment_bytes is None:
        st.error("⚠️ Please upload both a Person photo and a Garment image, or enable 'Use Demo Model & Garment' in the sidebar.")
    else:
        # Show loading spinner with status text
        with st.spinner("⚡ Connecting to backend server and running AI try-on pipeline... (This might take a moment if Hugging Face model is loading)"):
            try:
                # 1. Hit FastAPI Try-on Endpoint
                files = {
                    "person": ("person.jpg", person_bytes, "image/jpeg"),
                    "garment": ("garment.jpg", garment_bytes, "image/jpeg")
                }
                data = {
                    "garment_description": garment_desc,
                    "category": category,
                    "denoise_steps": denoise_steps,
                    "seed": seed
                }
                
                tryon_url = f"{BACKEND_URL}/api/tryon"
                response = requests.post(tryon_url, files=files, data=data, timeout=90)
                
                if response.status_code == 200:
                    res_json = response.json()
                    result_url = res_json.get("result_url")
                    is_real_ai = res_json.get("is_real_ai", False)
                    message = res_json.get("message", "")
                    
                    full_result_url = f"{BACKEND_URL}{result_url}"
                    
                    st.markdown("---")
                    st.markdown("## 🏆 Generated Try-On Result")
                    
                    res_col1, res_col2 = st.columns([2, 1])
                    
                    with res_col1:
                        # Display output badge based on active model engine
                        if is_real_ai:
                            st.markdown('<div class="ai-badge">🟢 HF IDM-VTON Active</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="fallback-badge">🟡 PIL Overlay Fallback Active</div>', unsafe_allow_html=True)
                        
                        # Load and display generated image
                        st.image(full_result_url, caption="Your AI Try-On Preview", use_container_width=True)
                        st.success(message)
                        
                    with res_col2:
                        st.markdown("### Style Insights")
                        st.markdown(f"**Garment**: {garment_desc}")
                        st.markdown(f"**Category**: {category.replace('_', ' ').title()}")
                        st.markdown(f"**Seed**: {seed}")
                        st.markdown(f"**Denoise Steps**: {denoise_steps}")
                        st.info("💡 Pro-Tip: Try adjusting the description or using different lighting files to tweak the blend style.")
                        
                else:
                    st.error(f"❌ Backend returned error code {response.status_code}: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to the FastAPI backend. Make sure the backend server is running on port 8000.")
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")

        # 2. Fetch and render outfit recommendations regardless of tryon engine status
        with st.spinner("🔍 Curating matching accessories..."):
            try:
                rec_url = f"{BACKEND_URL}/api/recommendations"
                rec_response = requests.get(
                    rec_url, 
                    params={"garment_description": garment_desc, "category": category},
                    timeout=10
                )
                
                if rec_response.status_code == 200:
                    recommendations = rec_response.json()
                    
                    st.markdown("---")
                    st.markdown("## 👜 Recommended Matching Accessories")
                    st.write("Complete the look with these handpicked items matching your style profile:")
                    
                    # Layout grid
                    rec_cols = st.columns(3)
                    
                    for idx, item in enumerate(recommendations):
                        col = rec_cols[idx % 3]
                        with col:
                            # Prepend backend server URL to fetch asset image
                            full_item_img = f"{BACKEND_URL}{item['image_url']}"
                            style_class = f"badge-{item['style_tag']}"
                            
                            card_html = f"""
                            <div class="accessory-card">
                                <div class="accessory-img-container">
                                    <img src="{full_item_img}" class="accessory-img">
                                </div>
                                <div>
                                    <span class="badge {style_class}">{item['style_tag']}</span>
                                    <div class="accessory-title">{item['name']}</div>
                                    <div class="accessory-price">{item['price']}</div>
                                    <div class="accessory-desc">{item['description']}</div>
                                </div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.warning("Could not fetch recommendations at this time.")
            except Exception as e:
                st.warning(f"Error fetching recommendations: {str(e)}")
else:
    # Initial load placeholder info
    st.markdown("---")
    st.markdown("### 💡 How to use:")
    st.markdown("""
    1. Upload a portrait/photo of a person in the left box.
    2. Upload a flat lay/clear image of a garment (shirt, dress, t-shirt) in the right box.
    3. (Optional) Check the **Use Demo Model & Garment** checkbox in the sidebar for a quick demo.
    4. Write a brief description of the garment to help match matching accessories.
    5. Click **Generate Try-On** to view the outfit preview and personalized accessories recommendations!
    """)
