from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime, timedelta
import random
import string

class TestDataGenerator:
    def __init__(self, output_dir: str = "test_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_license_image(self, 
                             name: str = None,
                             license_number: str = None,
                             expiry_date: str = None,
                             license_class: str = None) -> str:
        """Generate a test driver's license image with specified or random data"""
        # Create a new image with white background
        img = Image.new('RGB', (800, 500), color='white')
        draw = ImageDraw.Draw(img)
        
        # Generate random data if not provided
        name = name or self._generate_name()
        license_number = license_number or self._generate_license_number()
        expiry_date = expiry_date or self._generate_future_date()
        license_class = license_class or random.choice(['A', 'B', 'C'])
        
        # Draw text on image
        draw.text((50, 100), f"NAME: {name}", fill='black')
        draw.text((50, 150), f"LICENSE: {license_number}", fill='black')
        draw.text((50, 200), f"CLASS: {license_class}", fill='black')
        draw.text((50, 250), f"EXPIRY: {expiry_date}", fill='black')
        
        # Save image
        filename = os.path.join(self.output_dir, f"test_license_{license_number}.png")
        img.save(filename)
        return filename

    def _generate_name(self) -> str:
        """Generate a random name"""
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def _generate_license_number(self) -> str:
        """Generate a random license number"""
        letter = random.choice(string.ascii_uppercase)
        numbers = ''.join(random.choices(string.digits, k=7))
        return f"{letter}{numbers}"

    def _generate_future_date(self) -> str:
        """Generate a future date within 5 years"""
        days = random.randint(1, 365 * 5)  # Up to 5 years in the future
        future_date = datetime.now() + timedelta(days=days)
        return future_date.strftime("%Y-%m-%d")

    def generate_expired_license(self) -> str:
        """Generate an expired license image"""
        past_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
        return self.generate_license_image(expiry_date=past_date)

    def generate_invalid_class_license(self) -> str:
        """Generate a license with invalid class"""
        return self.generate_license_image(license_class='X')