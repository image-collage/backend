from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io
import os
import requests

app = Flask(__name__)
CORS(app)

# Ensure the "uploads" folder exists
os.makedirs("uploads", exist_ok=True)

def upload_image_to_imgbb(image_data, api_key):
    url = "https://api.imgbb.com/1/upload"
    payload = {
        'key': api_key
    }
    files = {
        'image': image_data
    }

    response = requests.post(url, data=payload, files=files)
    
    if response.status_code == 200:
        response_data = response.json()
        viewer_url = response_data['data']['url']
        direct_url = response_data['data']['url_viewer']
        return viewer_url, direct_url
    else:
        return None, None

def create_collage(images, watermark_text="onlyfans4you.in"):
    final_size = 1280
    border_size = 20
    single_image_size = (final_size - 3 * border_size) // 2

    resized_images = [img.resize((single_image_size, single_image_size), Image.Resampling.LANCZOS) for img in images]

    collage = Image.new('RGB', (final_size, final_size), color=(255, 255, 255))

    positions = [
        (border_size, border_size),
        (single_image_size + 2 * border_size, border_size),
        (border_size, single_image_size + 2 * border_size),
        (single_image_size + 2 * border_size, single_image_size + 2 * border_size)
    ]

    for img, pos in zip(resized_images, positions):
        collage.paste(img, pos)

    draw = ImageDraw.Draw(collage)

    # Independent font size
    font_size = 50  # Set a fixed font size
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Calculate the text position
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = (final_size - text_width - border_size, final_size - text_height - border_size)

    # Draw the watermark
    draw.text(position, watermark_text, fill=(0, 0, 0), font=font)

    # Save collage to BytesIO
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

    image_paths = []
    for i, file in enumerate(files):
        file_path = os.path.join('uploads', f"image_{i}.jpg")
        file.save(file_path)
        image_paths.append(file_path)

    images = [Image.open(path) for path in image_paths]
    collage_image = create_collage(images)

    # Upload the collage image to ImgBB
    api_key = "12ba489d64c740258b7de4b634d1b9ff"
    viewer_url, direct_url = upload_image_to_imgbb(collage_image, api_key)

    # Create the response with both URLs and the image blob
    return jsonify({
        "viewer_url": viewer_url,
        "direct_url": direct_url,
        "image_url": viewer_url  # You can also return the image URL for further use
    }), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
