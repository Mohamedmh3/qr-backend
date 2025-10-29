"""
QR Code generation utility for the QR Access Verification System.
Generates unique QR codes for user identification.
"""

import os
import qrcode
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
import string
import random

# Try to import PIL, but make it optional
try:
    from PIL import Image
    PIL_AVAILABLE = True
    print("PIL (Pillow) is available - PNG QR codes will be generated.")
except ImportError:
    PIL_AVAILABLE = False
    print("WARNING: Pillow (PIL) not installed. QR code image generation will be limited.")


def generate_unique_qr_id():
    """
    Generate a unique QR ID in the format QR-XXXXXXXX
    where X is an alphanumeric character.
    
    Returns:
        str: Unique QR ID (e.g., 'QR-A1B2C3D4')
    """
    characters = string.ascii_uppercase + string.digits
    random_string = ''.join(random.choices(characters, k=8))
    return f"QR-{random_string}"


def generate_qr_code(qr_id, user_name=None):
    """
    Generate a QR code image for the given QR ID.

    Args:
        qr_id (str): The unique QR ID to encode
        user_name (str, optional): User name to include in the QR code

    Returns:
        tuple: (file_path, file_content) where file_path is the relative path
               and file_content is a ContentFile object
    """
    # Prepare QR code data
    qr_data = qr_id
    if user_name:
        qr_data = f"{qr_id}|{user_name}"

    # Try PIL/PNG first (best option)
    if PIL_AVAILABLE:
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Generate image
            img = qr.make_image(fill_color="black", back_color="white")
            if not isinstance(img, Image.Image):
                img = img.convert('RGB')

            # Convert to PNG
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            file_name = f"{qr_id}.png"
            file_path = os.path.join('qr_codes', file_name)
            file_content = ContentFile(buffer.read(), name=file_name)

            print(f"Generated PNG QR code: {file_path}")
            return file_path, file_content

        except Exception as e:
            print(f"PNG generation failed: {e}, trying fallback...")

    # Try SVG fallback
    try:
        import qrcode.image.svg
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
            image_factory=factory,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image()

        file_name = f"{qr_id}.svg"
        file_path = os.path.join('qr_codes', file_name)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Save SVG
        with open(full_path, 'w') as f:
            img.save(f)

        # Read back as content
        with open(full_path, "rb") as f:
            file_content = ContentFile(f.read(), name=file_name)

        print(f"Generated SVG QR code: {file_path}")
        return file_path, file_content

    except Exception as e:
        print(f"SVG generation failed: {e}")

    # Final fallback to text
    print(f"WARNING: Creating text-based QR ID file for {qr_id} (image generation failed)")
    file_name = f"{qr_id}.txt"
    file_path = os.path.join('qr_codes', file_name)
    text_content = f"QR ID: {qr_data}\nNote: Install Pillow for proper QR code images."
    file_content = ContentFile(text_content.encode(), name=file_name)
    return file_path, file_content


def get_qr_code_url(request, qr_id):
    """
    Find a QR code image file, prefer PNG, then SVG, else TXT. Return full URL using MEDIA_URL.
    """
    from django.conf import settings
    import os
    preferred = ["png", "svg", "txt"]
    for ext in preferred:
        file_path = f"qr_codes/{qr_id}.{ext}"
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if os.path.exists(full_path):
            if request:
                return request.build_absolute_uri(f"{settings.MEDIA_URL}{file_path}")
            else:
                return f"{settings.MEDIA_URL}{file_path}"
    return None


def delete_qr_code(qr_id):
    """
    Delete the QR code image file for a given QR ID.
    
    Args:
        qr_id (str): The QR ID
        
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', f"{qr_id}.png")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting QR code: {e}")
        return False
