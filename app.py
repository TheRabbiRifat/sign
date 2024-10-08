# Import necessary libraries
from flask import Flask, jsonify, request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random
from datetime import datetime
import io
import base64

app = Flask(__name__)

# Words to exclude in both languages
EXCLUDED_WORDS_BN = ["মোহাম্মদ", "মোঃ"]
EXCLUDED_WORDS_EN = ["Md", "Mohammad", "Mohammed"]

# Function to get a random font (adjust paths if needed)
def get_random_font(language):
    english_fonts = ["arial.ttf", "times.ttf"]  # Add paths to your English fonts
    bengali_fonts = ["Kobiguru.ttf", "Kobiguru.ttf"]  # Add paths to your Bengali fonts
    if language == "bn":
        font_path = random.choice(bengali_fonts)
    else:
        font_path = random.choice(english_fonts)

    try:
        font = ImageFont.truetype(font_path, 40)
    except IOError:
        font = ImageFont.load_default()

    return font

# Function to check language based on date_of_birth and occupation
def should_use_english(date_of_birth, occupation):
    dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
    return dob.year > 1980 and (occupation == "ছাত্র-ছাত্রী" or occupation == "বেসরকারি চাকরিজীবী")

# Function to filter out excluded words from the name
def filter_excluded_words(name, language):
    if language == "bn":
        words = [word for word in name.split() if word not in EXCLUDED_WORDS_BN]
    else:
        words = [word for word in name.split() if word not in EXCLUDED_WORDS_EN]
    return " ".join(words)

# Shortens the name based on language and length
def get_shortened_name(name, language):
    name = filter_excluded_words(name, language)
    if language == "bn":
        if len(name) <= 12:
            return name
        else:
            words = name.split()
            return words[0] if len(words[0]) <= 12 else words[-1]
    else:
        if len(name) <= 8:
            return name
        else:
            words = name.split()
            return words[0] if len(words[0]) <= 8 else words[-1]

# Generate fingerprint variation (add valid image paths)
def generate_fingerprint_variation():
    # You can upload or use valid image paths in Colab
    fingerprint_samples = ['finger_1.jpg', 'finger_2.jpg']  # Add valid paths for Colab
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

# Generate text image
def text_to_image(bengali_text, english_text, date_of_birth, occupation):
    width, height = 260, 130
    background_color = "white"

    # Create text image
    img = Image.new('RGBA', (width, height), background_color)

    language = "en" if should_use_english(date_of_birth, occupation) else "bn"
    text = english_text if language == "en" else bengali_text
    font = get_random_font(language)
    text = get_shortened_name(text, language)

    text_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_img)

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((width - text_width) // 2, (height - text_height) // 2)

    draw.text(position, text, font=font, fill=(0, 0, 0, 200))
    angle = random.uniform(-2, 2)
    rotated_text_img = text_img.rotate(angle, expand=1, resample=Image.BICUBIC)

    rotated_width, rotated_height = rotated_text_img.size
    paste_position = ((width - rotated_width) // 2, (height - rotated_height) // 2)

    img.paste(rotated_text_img, paste_position, rotated_text_img)

    img = img.convert("RGB")

    # Save image to a bytes buffer
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)

    return base64.b64encode(buffered.getvalue()).decode()

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
    english_text = data.get('english_text', '')
    date_of_birth = data.get('date_of_birth', '')
    occupation = data.get('occupation', '')

    # Generate text image
    text_image_base64 = text_to_image(bengali_text, english_text, date_of_birth, occupation)

    # Generate fingerprint image
    fingerprint_image = generate_fingerprint_variation()
    fingerprint_image_base64 = image_to_base64(fingerprint_image)

    # Prepend the base64 data with the MIME type for a Data URI
    text_image_data_uri = f"data:image/png;base64,{text_image_base64}"
    fingerprint_image_data_uri = f"data:image/png;base64,{fingerprint_image_base64}"

    # Return the images as Data URIs in JSON response
    return jsonify({
        'sign': text_image_data_uri ,
        'fingerprint': fingerprint_image_data_uri
    })

# Start Flask app on 0.0.0.0 so it can be accessed externally
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
          
