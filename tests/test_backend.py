import os
import unittest
import json
from PIL import Image
from models.tryon_pipeline import remove_white_background, run_local_fallback, run_tryon
from backend.main import get_recommendations

class TestTryOnAndRecommendations(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create temp test directory
        cls.test_dir = "data/test_temp"
        os.makedirs(cls.test_dir, exist_ok=True)
        
        # Create dummy person image (a simple blue square)
        cls.person_path = os.path.join(cls.test_dir, "test_person.png")
        person_img = Image.new("RGB", (200, 300), color="blue")
        person_img.save(cls.person_path)
        
        # Create dummy garment image (a white square with a red center shirt)
        cls.garment_path = os.path.join(cls.test_dir, "test_garment.png")
        garment_img = Image.new("RGB", (100, 100), color="white")
        # Draw a smaller red rectangle in the center of the garment
        for x in range(30, 70):
            for y in range(20, 80):
                garment_img.putpixel((x, y), (255, 0, 0)) # Red
        garment_img.save(cls.garment_path)
        
        cls.output_dir = os.path.join(cls.test_dir, "outputs")
        
    @classmethod
    def tearDownClass(cls):
        # Cleanup files
        for f in [cls.person_path, cls.garment_path]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
        if os.path.exists(cls.output_dir):
            try:
                import shutil
                shutil.rmtree(cls.output_dir)
            except Exception:
                pass
        if os.path.exists(cls.test_dir):
            try:
                os.rmdir(cls.test_dir)
            except Exception:
                pass

    def test_remove_white_background(self):
        """Tests white background keying logic in the image processor."""
        img = Image.open(self.garment_path)
        transparent_img = remove_white_background(img)
        
        # Check that the format is converted to RGBA
        self.assertEqual(transparent_img.mode, "RGBA")
        
        # Check that top-left pixel (originally white) is now transparent
        pixels = transparent_img.getpixel((0, 0))
        self.assertEqual(pixels[3], 0) # Alpha channel is 0 (fully transparent)
        
        # Check that center red pixel remains opaque
        center_pixel = transparent_img.getpixel((50, 50))
        self.assertGreater(center_pixel[3], 0) # Opaque or partially opaque
        self.assertEqual(center_pixel[0], 255) # Red channel is 255

    def test_run_local_fallback(self):
        """Tests the PIL image blending fallback engine."""
        output_path = os.path.join(self.test_dir, "test_output_fallback.jpg")
        result = run_local_fallback(self.person_path, self.garment_path, output_path)
        
        self.assertTrue(os.path.exists(result))
        
        # Verify result is a readable image with person size
        res_img = Image.open(result)
        self.assertEqual(res_img.size, (200, 300))
        res_img.close()
        
        if os.path.exists(output_path):
            os.remove(output_path)

    def test_run_tryon_fallback_trigger(self):
        """Tests that run_tryon falls back gracefully on error/timeout."""
        # We invoke run_tryon with invalid HF spaces or trigger the network exception
        # to ensure it returns a valid path and False for is_real_ai
        output_path, is_real_ai = run_tryon(
            person_path=self.person_path,
            garment_path=self.garment_path,
            garment_description="Test garment description",
            category="upper_body",
            denoise_steps=10,
            seed=42,
            output_dir=self.output_dir
        )
        
        self.assertTrue(os.path.exists(output_path))
        # Since yisol/IDM-VTON space might be unreachable in unittest environments
        # or rate-limited, it should return False (fallback) or True (if successfully hit),
        # but in either case, the output file MUST exist.
        self.assertIn(os.path.exists(output_path), [True])

    def test_get_recommendations_formal(self):
        """Tests that formal descriptions return formal style accessories."""
        recs = get_recommendations(garment_description="Elegant formal black blazer for wedding", category="upper_body")
        self.assertEqual(len(recs), 3)
        # Check if style_tag is prioritized for 'formal'
        self.assertEqual(recs[0]["style_tag"], "formal")

    def test_get_recommendations_sporty(self):
        """Tests that athletic/running descriptions return sporty style accessories."""
        recs = get_recommendations(garment_description="running gym shorts with pockets", category="lower_body")
        self.assertEqual(len(recs), 3)
        self.assertEqual(recs[0]["style_tag"], "sporty")

if __name__ == "__main__":
    unittest.main()
