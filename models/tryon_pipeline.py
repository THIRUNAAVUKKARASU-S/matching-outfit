import os
import time
import logging
import numpy as np
from PIL import Image, ImageOps, ImageFilter
from gradio_client import Client, handle_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tryon_pipeline")

def remove_white_background(img: Image.Image, threshold: int = 240) -> Image.Image:
    """
    Helper function to remove solid white/light backgrounds from garment images.
    Converts close-to-white pixels to transparent. Uses numpy for high performance.
    """
    img = img.convert("RGBA")
    data = np.array(img)
    
    # Extract R, G, B channels
    r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]
    
    # Mask pixels that are close to white across all three channels
    white_mask = (r >= threshold) & (g >= threshold) & (b >= threshold)
    
    # Set those pixels to transparent white
    data[white_mask] = [255, 255, 255, 0]
    
    # Reconstruct the image
    img = Image.fromarray(data)
    
    # Smooth edges using a minor gaussian blur on the alpha channel
    alpha = img.split()[3]
    alpha = alpha.filter(ImageFilter.GaussianBlur(1.0))
    img.putalpha(alpha)
    
    return img

def run_local_fallback(person_path: str, garment_path: str, output_path: str) -> str:
    """
    Performs a local PIL overlay try-on simulation when API is offline.
    Places the garment over the center torso of the person image.
    """
    logger.info("Executing local PIL Try-On fallback overlay...")
    try:
        person_img = Image.open(person_path).convert("RGBA")
        garment_img = Image.open(garment_path).convert("RGBA")
        
        p_width, p_height = person_img.size
        
        # Clean white background from garment if any
        garment_img = remove_white_background(garment_img)
        
        # Calculate target size for the garment (approx. 40% width and 35% height of the person)
        target_width = int(p_width * 0.45)
        # Maintain aspect ratio
        g_w, g_h = garment_img.size
        aspect_ratio = g_h / g_w
        target_height = int(target_width * aspect_ratio)
        
        # Limit height if it gets too long
        max_height = int(p_height * 0.40)
        if target_height > max_height:
            target_height = max_height
            target_width = int(target_height / aspect_ratio)
            
        garment_resized = garment_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Position garment over the torso
        # Torso is roughly horizontally centered and positioned vertically around 40-50% down
        x_pos = (p_width - target_width) // 2
        y_pos = int(p_height * 0.42)
        
        # Paste the garment onto the person image using the garment's alpha channel
        combined = Image.new("RGBA", person_img.size)
        combined.paste(person_img, (0, 0))
        combined.paste(garment_resized, (x_pos, y_pos), garment_resized)
        
        # Save as RGB JPEG
        combined.convert("RGB").save(output_path, "JPEG", quality=95)
        logger.info(f"Fallback try-on image saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error executing local fallback: {str(e)}")
        # If fallback also fails, just copy the person image as a last resort
        img = Image.open(person_path).convert("RGB")
        img.save(output_path, "JPEG")
        return output_path

def run_tryon(
    person_path: str,
    garment_path: str,
    garment_description: str = "clothing item",
    category: str = "upper_body",
    denoise_steps: int = 30,
    seed: int = 42,
    output_dir: str = "data/outputs"
) -> tuple[str, bool]:
    """
    Executes virtual try-on using Hugging Face IDM-VTON.
    Falls back to PIL overlay blending if the Hugging Face API fails.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"tryon_{int(time.time())}.jpg"
    output_path = os.path.join(output_dir, filename)
    
    # Check if files exist
    if not os.path.exists(person_path):
        raise FileNotFoundError(f"Person image not found: {person_path}")
    if not os.path.exists(garment_path):
        raise FileNotFoundError(f"Garment image not found: {garment_path}")
        
    try:
        logger.info("Connecting to Hugging Face IDM-VTON Space...")
        # yisol/IDM-VTON is the standard HF space for IDM-VTON tryon
        client = Client("yisol/IDM-VTON")
        
        logger.info("Sending job to Gradio API...")
        # Set up parameters required for yisol/IDM-VTON /tryon endpoint
        result = client.predict(
            dict={
                "background": handle_file(person_path),
                "layers": [],
                "composite": None
            },
            garm_img=handle_file(garment_path),
            garment_des=garment_description,
            is_checked=True,
            is_checked_crop=False,
            denoise_steps=denoise_steps,
            seed=seed,
            api_name="/tryon"
        )
        
        # The API returns a list or string of outputs, typically the first element is the try-on image path
        if isinstance(result, tuple) or isinstance(result, list):
            result_img_path = result[0]
        else:
            result_img_path = result
            
        if result_img_path and os.path.exists(result_img_path):
            img = Image.open(result_img_path).convert("RGB")
            img.save(output_path, "JPEG")
            logger.info(f"API try-on successful. Saved to {output_path}")
            return output_path, True
        else:
            raise Exception("Gradio client did not return a valid result path.")
            
    except Exception as e:
        logger.warning(f"IDM-VTON API execution failed or timed out: {str(e)}")
        # Run local fallback
        fallback_path = run_local_fallback(person_path, garment_path, output_path)
        return fallback_path, False
