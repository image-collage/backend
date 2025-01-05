from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io
import os
import requests

app = Flask(__name__)

# Enable CORS for all domains (you can restrict this later for security)
CORS(app)

# Ensure the "uploads" folder exists
os.makedirs("uploads", exist_ok=True)

def upload_image_to_imgbb(image_path, api_key):
    # Open the image to upload
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # Define the URL for ImgBB API
    url = "https://api.imgbb.com/1/upload"

    # Prepare data for the request
    payload = {
        'key': api_key
    }
    files = {
        'image': image_data
    }

    # Make the request to upload the image
    response = requests.post(url, data=payload, files=files)

    # Check if the upload was successful
    if response.status_code == 200:
        response_data = response.json()
        viewer_url = response_data['data']['url']  # Viewer URL
        direct_url = response_data['data']['url_viewer']  # Direct URL
        print(f"Image uploaded successfully!")
        print(f"Viewer URL: {viewer_url}")
        print(f"Direct URL: {direct_url}")
        return viewer_url, direct_url
    else:
        print(f"Error uploading image: {response.status_code}")
        return None, None

def create_collage(images, watermark_text="onlyfans4you.in"):
    # Define final image size and white border size
    final_size = 1280
    border_size = 20

    # Calculate the size for each individual image with borders
    single_image_size = (final_size - 3 * border_size) // 2

    # Resize all images to the calculated size
    resized_images = [img.resize((single_image_size, single_image_size), Image.Resampling.LANCZOS) for img in images]

    # Create a blank white canvas for the collage
    collage = Image.new('RGB', (final_size, final_size), color=(255, 255, 255))

    # Calculate positions for each image
    positions = [
        (border_size, border_size),
        (single_image_size + 2 * border_size, border_size),
        (border_size, single_image_size + 2 * border_size),
        (single_image_size + 2 * border_size, single_image_size + 2 * border_size)
    ]

    # Paste resized images with borders onto the collage
    for img, pos in zip(resized_images, positions):
        collage.paste(img, pos)

    # Add watermark text at the bottom-right corner of the white border
    draw = ImageDraw.Draw(collage)
    font_size = border_size * 2  # Make the font size proportional to the border size
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Calculate the position for the watermark
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = (final_size - text_width - border_size, final_size - text_height - border_size)

    # Draw the watermark in bold and black
    draw.text(position, watermark_text, fill=(0, 0, 0), font=font)

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
    images = [Image.open(path) for path in image_paths]
    collage_image = create_collage(images)

    # Upload collage to ImgBB
    api_key = "12ba489d64c740258b7de4b634d1b9ff"  # Replace with your actual API key
    viewer_url, direct_url = upload_image_to_imgbb(image_paths[0], api_key)

    # Save the collage image to a file to return as download
    collage_image_path = os.path.join('uploads', 'collage.jpg')
    collage_image.save(collage_image_path)

    # Return the file for download and URLs in JSON
    response = jsonify({
        "viewer_url": viewer_url,
        "direct_url": direct_url
    })
    response.headers['Content-Disposition'] = 'attachment; filename=collage.jpg'
    response.set_data(open(collage_image_path, 'rb').read())

    return response

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)  # Make sure it listens on all network interfaces
