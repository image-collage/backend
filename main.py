from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # Add CORS
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)

# Enable CORS for all domains (you can restrict this later for security)
CORS(app)

# Ensure the "uploads" folder exists
os.makedirs("uploads", exist_ok=True)

def create_collage(images):
    # Assuming you are processing images to create a 2x2 collage
    collage_width = 1280
    collage_height = 1280
    collage = Image.new('RGB', (collage_width, collage_height), (255, 255, 255))

    # Resize images and place them in the collage
    images_resized = []
    for image in images:
        img = Image.open(image)
        img = img.resize((640, 640))
        images_resized.append(img)

    # Paste images into the collage
    collage.paste(images_resized[0], (0, 0))
    collage.paste(images_resized[1], (640, 0))
    collage.paste(images_resized[2], (0, 640))
    collage.paste(images_resized[3], (640, 640))

    # Add watermark text ("onlyfans4you.in") at the bottom-right corner
    draw = ImageDraw.Draw(collage)
    font = ImageFont.load_default()  # You can also use a custom font (e.g., truetype font)
    
    text = "onlyfans4you.in"
    font_size = 50  # Set a visible font size
    try:
        font = ImageFont.truetype("arial.ttf", font_size)  # Use a specific font
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font if arial is not available
    
    # Calculate text size and position
    text_width, text_height = draw.textsize(text, font)
    position = (collage_width - text_width - 10, collage_height - text_height - 10)  # 10px padding from the right and bottom

    # Draw text on the image
    draw.text(position, text, font=font, fill=(0, 0, 0))  # Black text color

    # Save the collage to a byte stream
    img_io = io.BytesIO()
    collage.save(img_io, 'JPEG')
    img_io.seek(0)
    
    return img_io

@app.route('/create-collage/', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({"error": "No files found"}), 400
    
    files = request.files.getlist('files')
    if len(files) != 4:
        return jsonify({"error": "Please upload exactly 4 images."}), 400

    # Save uploaded images
    image_paths = []
    for i, file in enumerate(files):
        file_path = os.path.join('uploads', f"image_{i}.jpg")
        file.save(file_path)
        image_paths.append(file_path)

    # Create collage and return the image
    collage_image = create_collage(image_paths)
    return send_file(collage_image, mimetype='image/jpeg', as_attachment=True, download_name='collage.jpg')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)  # Make sure it listens on all network interfaces
