from flask import Flask, request, jsonify, send_file
from PIL import Image
import io
import os

app = Flask(__name__)

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

    # Add watermark
    watermark = Image.new('RGB', (collage_width, collage_height), (255, 255, 255))
    watermark_img = Image.open("watermark.png")  # Use your watermark image here
    watermark.paste(watermark_img, (collage_width - 160, collage_height - 80))
    collage.paste(watermark, (0, 0), watermark)

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
    app.run(debug=True)
