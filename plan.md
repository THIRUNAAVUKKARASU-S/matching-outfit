# E-Commerce Virtual Try-On & Outfit Generator - System Architecture

This project is a complete prototype for an E-Commerce Virtual Try-On & Outfit Generator app.

## Project Structure
```
c:/Users/sthir/OneDrive/Documents/New folder (4)/
├── backend/
│   └── main.py              # FastAPI server handling API routes
├── data/
│   └── accessories.json     # Mock database for outfit recommendation matching
├── frontend/
│   └── app.py               # Streamlit application for uploading photos and UI layout
├── models/
│   └── tryon_pipeline.py    # Interface to HF IDM-VTON Space and image processing fallback
├── tests/
│   └── test_backend.py      # Automated request lifecycle testing
├── requirements.txt         # Project dependencies
└── plan.md                  # Project system architecture definition (this file)
```

## Component Details

### 1. Frontend: Streamlit (`frontend/app.py`)
Provides an interactive, visually pleasing interface where:
*   Users can upload a person image and a garment image side-by-side.
*   Users can choose parameters like denoise steps, crop options, and garment description.
*   A "Generate Try-On" button triggers backend processing with step-by-step progress spinners.
*   Outputs are rendered side-by-side (original inputs and resulting output).
*   A grid of outfit recommendations is shown underneath with badges, prices, and matching style indicators.

### 2. Backend: FastAPI (`backend/main.py`)
Acts as the central router and data orchestrator:
*   `POST /api/tryon`: Accepts person and garment multipart files, feeds them to `tryon_pipeline`, and returns the blended result.
*   `GET /api/recommendations`: Accepts garment type, text description, or tag, matching against the accessories database to return the top 3 items.

### 3. Models Pipeline (`models/tryon_pipeline.py`)
Interactions with the AI virtual try-on engine:
*   **Primary Engine**: Gradio Client calling `yisol/IDM-VTON` Hugging Face Space.
*   **Fallback Engine**: Local PIL/OpenCV-based image blender that extracts/resizes the garment image and overlays it on the person's torso region using transparency masking. This ensures the app is testable even offline or when HF is overloaded.

### 4. Recommendation Engine
*   Checks the environment for AI API keys (like `GEMINI_API_KEY` or `OPENAI_API_KEY`). If found, uses a lightweight LLM prompt to select accessories.
*   If no key is present, defaults to a semantic tag matching algorithm that compares style tags (e.g. "sporty", "casual", "formal") and categories to recommend appropriate bags, shoes, and sunglasses.
