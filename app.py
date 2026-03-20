import os
import random
import string
import io

from flask import Flask, session, render_template, redirect, url_for, request, send_file, make_response
from PIL import Image, ImageDraw, ImageFont, ImageFilter

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Characters excluding ambiguous ones (0/O, 1/I/l)
CAPTCHA_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'


def generate_captcha_text(length=7):
    """Generate a random captcha string."""
    return ''.join(random.choices(CAPTCHA_CHARS, k=length))


def create_captcha_image(text):
    """Render distorted captcha text as a PNG image."""
    width, height = 280, 80
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Try to load a bold font, fall back to default
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 42)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 42)
        except (OSError, IOError):
            font = ImageFont.load_default(size=42)

    # Draw each character individually with random offsets and rotation
    char_width = width // (len(text) + 1)
    for i, char in enumerate(text):
        # Create a temporary image for this character
        char_img = Image.new('RGBA', (50, 60), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_img)

        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        char_draw.text((5, 5), char, font=font, fill=color)

        # Rotate the character
        angle = random.randint(-25, 25)
        char_img = char_img.rotate(angle, expand=True, fillcolor=(255, 255, 255, 0))

        # Paste onto main image
        x = 10 + i * char_width
        y = random.randint(0, 15)
        image.paste(char_img, (x, y), char_img)

    # Add noise lines
    for _ in range(random.randint(3, 5)):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)

    # Add noise dots
    for _ in range(100):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        color = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
        draw.point((x, y), fill=color)

    # Apply slight blur
    image = image.filter(ImageFilter.GaussianBlur(radius=1.0))

    # Save to buffer
    buffer = io.BytesIO()
    image.save(buffer, 'PNG')
    buffer.seek(0)
    return buffer


@app.route('/')
def index():
    """Serve the main captcha page."""
    # Generate new captcha on every page load
    captcha_text = generate_captcha_text()
    session['captcha_text'] = captcha_text

    # Get flash message if any
    message = session.pop('message', None)
    message_type = session.pop('message_type', None)

    return render_template('index.html', message=message, message_type=message_type)


@app.route('/captcha-image')
def captcha_image():
    """Serve the captcha image as PNG."""
    text = session.get('captcha_text', '')
    if not text:
        text = generate_captcha_text()
        session['captcha_text'] = text

    buffer = create_captcha_image(text)
    response = make_response(send_file(buffer, mimetype='image/png'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


@app.route('/submit', methods=['POST'])
def submit():
    """Validate the captcha input."""
    user_input = request.form.get('captcha_input', '')
    captcha_text = session.get('captcha_text', '')

    if user_input == captcha_text:
        session['message'] = 'Captcha verified successfully!'
        session['message_type'] = 'success'
    else:
        session['message'] = 'Incorrect captcha. Please try again.'
        session['message_type'] = 'error'

    return redirect(url_for('index'))


@app.route('/refresh')
def refresh():
    """Refresh the captcha."""
    session.pop('message', None)
    session.pop('message_type', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
