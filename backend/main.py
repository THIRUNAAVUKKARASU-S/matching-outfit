import os
import json
import uuid
import shutil
import logging
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from models.tryon_pipeline import run_tryon

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend_main")

app = FastAPI(
    title="Virtual Try-On & Outfit Generator API",
    description="Backend API for overlaying garments and recommending matching accessories",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
TEMP_DIR = "data/temp"
OUTPUT_DIR = "data/outputs"
IMAGES_DIR = "data/images"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Mount static files to serve product and generated images
# This allows the frontend to fetch images via HTTP e.g., http://localhost:8000/static/images/leather_handbag.png
app.mount("/static", StaticFiles(directory="data"), name="static")


class Accessory(BaseModel):
    id: int
    name: str
    category: str
    image_url: str
    style_tag: str
    price: str
    description: str


@app.get("/")
def read_root():
    return {"message": "Virtual Try-On & Outfit Generator API is running."}


@app.post("/api/tryon")
async def tryon_endpoint(
    person: UploadFile = File(...),
    garment: UploadFile = File(...),
    garment_description: str = Form("clothing item"),
    category: str = Form("upper_body"),
    denoise_steps: int = Form(30),
    seed: int = Form(42)
):
    """
    Accepts person and garment image uploads, performs tryon mapping,
    and returns the processed image path along with AI status metadata.
    """
    session_id = str(uuid.uuid4())
    person_temp_path = os.path.join(TEMP_DIR, f"{session_id}_person.jpg")
    garment_temp_path = os.path.join(TEMP_DIR, f"{session_id}_garment.jpg")
    
    try:
        # Save person upload file to temp directory
        with open(person_temp_path, "wb") as buffer:
            shutil.copyfileobj(person.file, buffer)
            
        # Save garment upload file to temp directory
        with open(garment_temp_path, "wb") as buffer:
            shutil.copyfileobj(garment.file, buffer)
            
        logger.info(f"Received tryon request. Person: {person.filename}, Garment: {garment.filename}")
        
        # Execute the try-on pipeline
        output_path, is_real_ai = run_tryon(
            person_path=person_temp_path,
            garment_path=garment_temp_path,
            garment_description=garment_description,
            category=category,
            denoise_steps=denoise_steps,
            seed=seed,
            output_dir=OUTPUT_DIR
        )
        
        # Clean up temp upload files asynchronously
        # (We keep them until the run finishes, then we can remove them)
        try:
            os.remove(person_temp_path)
            os.remove(garment_temp_path)
        except Exception:
            pass
            
        # Build the HTTP response
        # Return headers to tell the frontend if fallback or real AI was used
        relative_output_path = os.path.relpath(output_path, start="data").replace("\\", "/")
        static_url = f"/static/{relative_output_path}"
        
        return JSONResponse(
            content={
                "success": True,
                "result_url": static_url,
                "is_real_ai": is_real_ai,
                "message": "Generation completed successfully." if is_real_ai else "Completed using PIL Blending Fallback Engine."
            }
        )
        
    except Exception as e:
        logger.error(f"Error in tryon_endpoint: {str(e)}")
        # Clean up temp files if they still exist
        for path in [person_temp_path, garment_temp_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
        raise HTTPException(status_code=500, detail=f"Failed to process tryon: {str(e)}")


@app.get("/api/recommendations", response_model=List[Accessory])
def get_recommendations(
    garment_description: Optional[str] = "",
    category: Optional[str] = "upper_body"
):
    """
    Analyzes the garment description or category and queries the mock accessories JSON database
    to return the top 3 matching items.
    """
    accessories_file = "data/accessories.json"
    if not os.path.exists(accessories_file):
        raise HTTPException(status_code=500, detail="Accessories catalog database not found.")
        
    try:
        with open(accessories_file, "r") as f:
            catalog = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading catalog: {str(e)}")
        
    # Standardize style inputs to match tag keywords
    desc_lower = (garment_description or "").lower()
    
    # Simple semantic heuristics for matching garment style tags
    detected_style = "casual" # Default fallback style
    
    formal_keywords = ["formal", "suit", "blazer", "dress shirt", "trousers", "wedding", "office", "tuxedo", "business", "gown"]
    sporty_keywords = ["sporty", "gym", "running", "athletic", "tracksuit", "shorts", "sweatshirt", "hoodie", "jersey", "yoga"]
    
    if any(keyword in desc_lower for keyword in formal_keywords) or category in ["dresses"]:
        detected_style = "formal"
    elif any(keyword in desc_lower for keyword in sporty_keywords):
        detected_style = "sporty"
    elif "casual" in desc_lower or "t-shirt" in desc_lower or "jeans" in desc_lower or "denim" in desc_lower:
        detected_style = "casual"
        
    logger.info(f"Garment description: '{garment_description}', inferred style: '{detected_style}'")
    
    # Filter and rank accessories by style match
    matches = []
    other_items = []
    
    for item in catalog:
        # Construct full URL for product images
        # e.g., /static/images/leather_handbag.png
        relative_path = item["image_path"].replace("data/", "")
        img_url = f"/static/{relative_path}"
        
        accessory_item = {
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "image_url": img_url,
            "style_tag": item["style_tag"],
            "price": item["price"],
            "description": item["description"]
        }
        
        if item["style_tag"] == detected_style:
            matches.append(accessory_item)
        else:
            other_items.append(accessory_item)
            
    # Mix matches and other items to always return exactly 3 accessories
    # Prioritize exact style matches, then backfill with items from other categories
    final_recommendations = matches[:3]
    if len(final_recommendations) < 3:
        needed = 3 - len(final_recommendations)
        final_recommendations.extend(other_items[:needed])
        
    return final_recommendations
