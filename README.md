# E-Commerce Virtual Try-On & Outfit Generator

A complete interactive web prototype that allows users to perform **AI-driven Virtual Try-On** and receive smart **Outfit Recommendations** matching their styles.

The application leverages a modern two-tier architecture:
- **Frontend**: A highly responsive, visual, and user-friendly interface built with **Streamlit**.
- **Backend**: A high-performance **FastAPI** server that orchestrates AI inference and executes a recommendation algorithm.

---

## ✨ Features

- **AI-Powered Virtual Try-On**:
  - Blends a garment image onto a person's photo.
  - **Primary Inference**: Integrates directly with the `yisol/IDM-VTON` Hugging Face Space using the `gradio_client`.
  - **Local Fallback Engine**: If the Hugging Face Space is rate-limited, overloaded, or offline, the system seamlessly falls back to a custom Python PIL-based image processing algorithm to overlay the garment on the person's torso region.
- **Smart Outfit Recommendations**:
  - Dynamically recommends matching accessories (shoes, bags, sunglasses, etc.) based on the styling of the tried-on garment.
  - Features a **Dual Recommendation Engine**:
    - *AI-Driven Mode*: If an LLM API key (e.g., `GEMINI_API_KEY`) is present, it uses a lightweight model prompt to match and suggest styles.
    - *Heuristic Mode (Fallback)*: Analyzes style tags (e.g., `"sporty"`, `"formal"`, `"casual"`) from the description using semantic matches and returns appropriate matching items from a curated local database.
- **Modern User Interface**:
  - Real-time spinners, process feedback, side-by-side original/result image comparisons, and stylish badges for recommendations.
- **Comprehensive Testing Suite**:
  - Includes unit tests for the fallback processor, transparency-keying, and recommendation engine.

---

## 📂 Project Structure

```directory
c:/Users/sthir/OneDrive/Documents/New folder (4)/
├── backend/
│   └── main.py              # FastAPI server handling API routes and recommendations
├── data/
│   ├── accessories.json     # Mock database for outfit recommendation matching
│   └── images/              # Assets for local accessory items (e.g., white sneakers, leather handbag)
├── frontend/
│   └── app.py               # Streamlit application for photo upload and UI layout
├── models/
│   └── tryon_pipeline.py    # Interface to HF IDM-VTON Space / Local image processing fallback
├── tests/
│   └── test_backend.py      # Automated unit tests for background processing logic
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation (this file)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.8+** installed on your system.

### 2. Installation
Clone this repository and navigate to the project directory:
```bash
git clone https://github.com/THIRUNAAVUKKARASU-S/matching-outfit.git
cd matching-outfit
```

Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Running the Backend (FastAPI)
Start the FastAPI server on `http://127.0.0.1:8000`:
```bash
uvicorn backend.main:app --reload
```

### 4. Running the Frontend (Streamlit)
In a new terminal window, start the Streamlit web application:
```bash
streamlit run frontend/app.py
```
This will open the application in your default web browser at `http://localhost:8501`.

---

## 🧪 Testing

To run the automated test suite to ensure the try-on pipeline, background-keying, and recommendations work flawlessly:
```bash
python -m unittest tests/test_backend.py
```

---

## ⚙️ Configuration & API Integration

- By default, the application runs without external API keys using local rule-based recommendations.
- To enable AI-enhanced outfit recommendations, configure your environment keys:
  ```bash
  # Windows (Command Prompt)
  set GEMINI_API_KEY=your_gemini_api_key_here
  
  # Windows (PowerShell)
  $env:GEMINI_API_KEY="your_gemini_api_key_here"
  ```

---

## 🤝 Contributing
Contributions are welcome! Please fork the repository and open a pull request for any improvements, UI updates, or model integration enhancements.
