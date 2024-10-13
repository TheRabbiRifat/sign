from flask import Flask, jsonify, request
import random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from datetime import datetime
import io
import base64

app = Flask(__name__)

# Words to exclude in Bengali
EXCLUDED_WORDS_BN = ["মোহাম্মদ", "মোঃ"]

# Function to get a random Bengali font (adjust paths if needed)
def get_random_font():
    bengali_fonts = ["sing_v1.ttf"]  # Path to your Bengali font
    return random.choice(bengali_fonts)

# Function to filter out excluded words from the name
def filter_excluded_words(name):
    words = [word for word in name.split() if word not in EXCLUDED_WORDS_BN]
    return " ".join(words)

# Shortens the name based on length
def get_shortened_name(name):
    name = filter_excluded_words(name)
    if len(name) <= 12:
        return name
    else:
        words = name.split()
        return words[0] if len(words[0]) <= 12 else words[-1]

# Generate fingerprint variation (add valid image paths)
def generate_fingerprint_variation():
    # You can upload or use valid image paths
    fingerprint_samples = ['finger_1.jpg', 'finger_2.jpg']  # Add valid paths
    sample_image_path = random.choice(fingerprint_samples)
    sample_image = Image.open(sample_image_path)

    # Random transformations
    transformations = [
        lambda img: img.transpose(Image.FLIP_LEFT_RIGHT),
        lambda img: img.resize((random.randint(200, 250), random.randint(240, 280))),
        lambda img: img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0, 2)))  # Add blur
    ]

    # Apply a random transformation
    transformation = random.choice(transformations)
    modified_image = transformation(sample_image)

    # Increase contrast
    enhancer = ImageEnhance.Contrast(modified_image)
    modified_image = enhancer.enhance(3.0)

    return modified_image

# Generate text image with UTF-8 support using PIL
def text_to_image(bengali_text):
    # Ensure the text is properly encoded in UTF-8
    bengali_text = bengali_text.encode('utf-8').decode('utf-8')

    # Image size
    width, height = 260, 130
    background_color = (255, 255, 255)  # White background

    # Create a new image with white background
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # Load the Bengali font
    font_path = get_random_font()  # Path to your font file
    font = ImageFont.truetype(font_path, 40)  # Set font size

    # Calculate position for centering the text
    text_width, text_height = draw.textsize(bengali_text, font=font)
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw the text
    draw.text((x, y), bengali_text, font=font, fill=(0, 0, 0))  # Black text

    # Convert to base64 for output
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)

    return base64.b64encode(output.getvalue()).decode()

# Convert image to base64
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    buffered.seek(0)
    return base64.b64encode(buffered.getvalue()).decode()

@app.route('/check-json')
def check_json():
    return jsonify({"status": "success", "message": "Flask Sign Finger app is running!"})

@app.route('/generate_images', methods=['POST'])
def generate_images():
    data = request.json
    bengali_text = data.get('bengali_text', '')

    # Generate text image
    text_image_base64 = text_to_image(bengali_text)

    # Generate fingerprint image
    fingerprint_image = generate_fingerprint_variation()
    fingerprint_image_base64 = image_to_base64(fingerprint_image)

    # Prepend the base64 data with the MIME type for a Data URI
    text_image_data_uri = f"data:image/png;base64,{text_image_base64}"
    fingerprint_image_data_uri = f"data:image/png;base64,{fingerprint_image_base64}"

    # Return the images as Data URIs in JSON response
    return jsonify({
        'sign': text_image_data_uri,
        'fingerprint': fingerprint_image_data_uri
    })

# Start Flask app on 0.0.0.0 so it can be accessed externally
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
