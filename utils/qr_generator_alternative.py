"""
Alternative QR code generation without Pillow dependency.
Uses text-based QR codes and SVG generation as fallback.
"""

import qrcode
import qrcode.image.svg
from io import StringIO
import logging
import os
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_qr_code_alternative(qr_id, name):
    """
    Generate QR code using alternative methods without Pillow.
    
    Args:
        qr_id (str): Unique QR identifier
        name (str): User's name for the QR code
        
    Returns:
        tuple: (file_path, file_content)
    """
    try:
        # Method 1: Try SVG generation (no Pillow required)
        return generate_svg_qr_code(qr_id, name)
    except Exception as e:
        logger.warning(f"SVG QR generation failed: {e}")
        # Method 2: Fallback to text-based QR code
        return generate_text_qr_code(qr_id, name)


def generate_svg_qr_code(qr_id, name):
    """
    Generate SVG-based QR code.
    """
    try:
        # Create QR code with SVG factory
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
            image_factory=factory
        )
        
        # Add data to QR code
        qr_data = f"QR_ID:{qr_id}|NAME:{name}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create SVG image
        img = qr.make_image()
        
        # Save to string
        svg_string = StringIO()
        img.save(svg_string)
        svg_content = svg_string.getvalue()
        
        # Create file path
        file_path = f"qr_codes/{qr_id}.svg"
        
        # Ensure directory exists
        media_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(media_dir, exist_ok=True)
        
        # Save file
        full_path = os.path.join(media_dir, f"{qr_id}.svg")
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        logger.info(f"Generated SVG QR code: {full_path}")
        return file_path, svg_content
        
    except Exception as e:
        logger.error(f"SVG QR generation error: {e}")
        raise


def generate_text_qr_code(qr_id, name):
    """
    Generate text-based QR code as fallback.
    """
    try:
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=1
        )
        
        # Add data to QR code
        qr_data = f"QR_ID:{qr_id}|NAME:{name}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Generate text representation
        qr_text = qr.print_ascii(invert=True)
        
        # Create file path
        file_path = f"qr_codes/{qr_id}.txt"
        
        # Ensure directory exists
        media_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(media_dir, exist_ok=True)
        
        # Save file
        full_path = os.path.join(media_dir, f"{qr_id}.txt")
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(f"QR Code for: {name}\n")
            f.write(f"QR ID: {qr_id}\n")
            f.write("=" * 50 + "\n")
            f.write(qr_text)
            f.write("\n" + "=" * 50 + "\n")
            f.write(f"Scan this QR code or use the ID: {qr_id}\n")
        
        logger.info(f"Generated text QR code: {full_path}")
        return file_path, qr_text
        
    except Exception as e:
        logger.error(f"Text QR generation error: {e}")
        raise


def generate_html_qr_code(qr_id, name):
    """
    Generate HTML-based QR code with embedded SVG.
    """
    try:
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        
        # Add data to QR code
        qr_data = f"QR_ID:{qr_id}|NAME:{name}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Generate matrix
        matrix = qr.get_matrix()
        
        # Create HTML with CSS grid
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>QR Code - {name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; margin: 20px; }}
        .qr-container {{ display: inline-block; border: 2px solid #000; padding: 10px; }}
        .qr-grid {{ display: grid; grid-template-columns: repeat({len(matrix[0])}, 10px); gap: 0; }}
        .qr-cell {{ width: 10px; height: 10px; }}
        .qr-cell.filled {{ background-color: #000; }}
        .qr-cell.empty {{ background-color: #fff; }}
        .qr-info {{ margin-top: 20px; }}
    </style>
</head>
<body>
    <h2>QR Code for {name}</h2>
    <div class="qr-container">
        <div class="qr-grid">
"""
        
        # Add grid cells
        for row in matrix:
            for cell in row:
                cell_class = "filled" if cell else "empty"
                html_content += f'<div class="qr-cell {cell_class}"></div>\n'
        
        html_content += f"""
        </div>
    </div>
    <div class="qr-info">
        <p><strong>QR ID:</strong> {qr_id}</p>
        <p><strong>Name:</strong> {name}</p>
        <p>Scan this QR code or use the ID for verification.</p>
    </div>
</body>
</html>
"""
        
        # Create file path
        file_path = f"qr_codes/{qr_id}.html"
        
        # Ensure directory exists
        media_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(media_dir, exist_ok=True)
        
        # Save file
        full_path = os.path.join(media_dir, f"{qr_id}.html")
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML QR code: {full_path}")
        return file_path, html_content
        
    except Exception as e:
        logger.error(f"HTML QR generation error: {e}")
        raise


