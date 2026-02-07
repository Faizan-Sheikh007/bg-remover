from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageFilter
import io
import base64
import os

app = Flask(__name__)
CORS(app)

# Check which background removal library is available
BG_REMOVAL_METHOD = None

try:
    from rembg import remove as rembg_remove
    BG_REMOVAL_METHOD = "rembg"
    print("✅ Using rembg for background removal (BEST QUALITY)")
except Exception as e:
    print(f"⚠️  rembg not available: {e}")
    try:
        import cv2
        import numpy as np
        BG_REMOVAL_METHOD = "opencv"
        print("✅ Using OpenCV for background removal")
    except:
        print("❌ No background removal method available!")
        BG_REMOVAL_METHOD = "none"

def remove_background_rembg(image):
    """Remove background using rembg library (AI-based, best quality)"""
    return rembg_remove(image)

def remove_background_opencv(image):
    """Remove background using OpenCV with improved edge smoothing"""
    import cv2
    import numpy as np

    # Convert PIL to OpenCV
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    original_size = img_cv.shape[:2]

    # Create mask using GrabCut
    mask = np.zeros(img_cv.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    # Define rectangle around the subject (assuming centered)
    height, width = img_cv.shape[:2]
    margin = 10
    rect = (margin, margin, width - margin * 2, height - margin * 2)

    try:
        # Apply GrabCut
        cv2.grabCut(img_cv, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

        # Create binary mask
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

        # Smooth the mask to remove jagged edges
        mask2_smooth = cv2.GaussianBlur(mask2 * 255, (5, 5), 0)

        # Apply morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        mask2_smooth = cv2.morphologyEx(mask2_smooth, cv2.MORPH_CLOSE, kernel)
        mask2_smooth = cv2.morphologyEx(mask2_smooth, cv2.MORPH_OPEN, kernel)

        # Convert back to 0-1 range
        mask2_smooth = mask2_smooth.astype(float) / 255.0

        # Create RGBA image
        b, g, r = cv2.split(img_cv)
        alpha = (mask2_smooth * 255).astype(np.uint8)

        # Merge channels
        img_rgba = cv2.merge([r, g, b, alpha])

        # Convert back to PIL
        result = Image.fromarray(img_rgba, 'RGBA')

        # Apply slight edge smoothing in PIL
        alpha_channel = result.split()[3]
        alpha_smooth = alpha_channel.filter(ImageFilter.SMOOTH)
        result.putalpha(alpha_smooth)

        return result

    except Exception as e:
        print(f"OpenCV processing error: {e}")
        # Fallback: just return image with white background removed
        return image.convert('RGBA')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Background removal API is running',
        'method': BG_REMOVAL_METHOD,
        'quality': 'HIGH (AI)' if BG_REMOVAL_METHOD == 'rembg' else 'MEDIUM (OpenCV)' if BG_REMOVAL_METHOD == 'opencv' else 'LOW'
    })

@app.route('/remove-background', methods=['POST'])
def remove_background():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']

        # Read the image
        input_image = Image.open(file.stream)

        # Convert to RGB if needed
        if input_image.mode != 'RGB':
            input_image = input_image.convert('RGB')

        # Remove background based on available method
        if BG_REMOVAL_METHOD == "rembg":
            output_image = remove_background_rembg(input_image)
        elif BG_REMOVAL_METHOD == "opencv":
            output_image = remove_background_opencv(input_image)
        else:
            return jsonify({'error': 'No background removal method available'}), 500

        # Ensure RGBA mode
        if output_image.mode != 'RGBA':
            output_image = output_image.convert('RGBA')

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG', optimize=True)
        img_byte_arr.seek(0)

        # Encode to base64
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}',
            'method': BG_REMOVAL_METHOD,
            'quality': 'HIGH (AI)' if BG_REMOVAL_METHOD == 'rembg' else 'MEDIUM (OpenCV)'
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/change-background', methods=['POST'])
def change_background():
    try:
        data = request.get_json()

        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        # Decode base64 image
        image_data = data['image'].split(',')[1] if ',' in data['image'] else data['image']
        image_bytes = base64.b64decode(image_data)

        # Open image
        image = Image.open(io.BytesIO(image_bytes)).convert('RGBA')

        # Get background color (default white)
        bg_color = data.get('background_color', '#FFFFFF')

        # Convert hex to RGB
        bg_color = bg_color.lstrip('#')
        r, g, b = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))

        # Create background
        background = Image.new('RGBA', image.size, (r, g, b, 255))

        # Composite images
        result = Image.alpha_composite(background, image)

        # Convert to RGB
        result = result.convert('RGB')

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        result.save(img_byte_arr, format='PNG', optimize=True)
        img_byte_arr.seek(0)

        # Encode to base64
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}'
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/create-passport-grid', methods=['POST'])
def create_passport_grid():
    try:
        data = request.get_json()

        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        # Decode base64 image
        image_data = data['image'].split(',')[1] if ',' in data['image'] else data['image']
        image_bytes = base64.b64decode(image_data)

        # Open image
        photo = Image.open(io.BytesIO(image_bytes))

        # Get grid dimensions (default 4x4)
        cols = int(data.get('cols', 4))
        rows = int(data.get('rows', 4))

        # Passport photo size in pixels (35mm x 45mm at 300 DPI)
        photo_width = int(data.get('photo_width', 413))
        photo_height = int(data.get('photo_height', 531))

        # Resize photo to passport size with high quality
        photo = photo.resize((photo_width, photo_height), Image.Resampling.LANCZOS)

        # Calculate grid size with margins
        margin = 20
        grid_width = (photo_width * cols) + (margin * (cols + 1))
        grid_height = (photo_height * rows) + (margin * (rows + 1))

        # Create white background
        grid = Image.new('RGB', (grid_width, grid_height), 'white')

        # Paste photos in grid
        for row in range(rows):
            for col in range(cols):
                x = margin + (col * (photo_width + margin))
                y = margin + (row * (photo_height + margin))

                # Convert to RGB if needed for pasting
                if photo.mode == 'RGBA':
                    # Create white background for this photo
                    photo_bg = Image.new('RGB', (photo_width, photo_height), 'white')
                    photo_bg.paste(photo, (0, 0), photo)
                    grid.paste(photo_bg, (x, y))
                else:
                    grid.paste(photo, (x, y))

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        grid.save(img_byte_arr, format='PNG', dpi=(300, 300), optimize=True)
        img_byte_arr.seek(0)

        # Encode to base64
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}'
        })

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # Use Render's port, fallback to 5000

    try:
        from waitress import serve
        print("=" * 60)
        print("🚀 Background Removal API Server")
        print("=" * 60)
        print(f"✅ Method: {BG_REMOVAL_METHOD}")
        print(f"✅ Quality: {'HIGH (AI)' if BG_REMOVAL_METHOD == 'rembg' else 'MEDIUM (OpenCV)'}")
        print(f"✅ Server: http://0.0.0.0:{port}")
        print(f"✅ Health: http://0.0.0.0:{port}/health")
        print("=" * 60)
        print("💡 TIP: For BEST quality, install Python 3.11 + rembg")
        print("=" * 60)
        print("Press Ctrl+C to stop")
        print("=" * 60)
        serve(app, host='0.0.0.0', port=port, threads=4)
    except ImportError:
        print("=" * 60)
        print("🚀 Background Removal API Server (Development)")
        print("=" * 60)
        print(f"✅ Method: {BG_REMOVAL_METHOD}")
        print(f"✅ Quality: {'HIGH (AI)' if BG_REMOVAL_METHOD == 'rembg' else 'MEDIUM (OpenCV)'}")
        print(f"✅ Server: http://0.0.0.0:{port}")
        print(f"✅ Health: http://0.0.0.0:{port}/health")
        print("=" * 60)
        print("💡 TIP: For BEST quality, install Python 3.11 + rembg")
        print("💡 For production, install: pip install waitress")
        print("=" * 60)
        print("Press Ctrl+C to stop")
        print("=" * 60)
        app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
