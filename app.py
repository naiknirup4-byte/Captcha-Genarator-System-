import os, random, string, io
from flask import Flask, session, render_template, redirect, url_for, request, send_file, make_response
from PIL import Image, ImageDraw, ImageFont, ImageFilter

app = Flask(__name__)
app.secret_key = os.urandom(24)

CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'

def gen_text(n=7):
    return ''.join(random.choices(CHARS, k=n))

def gen_image(text):
    w, h = 280, 80
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 42)
    except:
        font = ImageFont.load_default()

    step = w // (len(text) + 1)

    for i, ch in enumerate(text):
        temp = Image.new('RGBA', (50, 60), (255, 255, 255, 0))
        d = ImageDraw.Draw(temp)
        d.text((5, 5), ch, font=font,
               fill=tuple(random.randint(0, 100) for _ in range(3)))
        temp = temp.rotate(random.randint(-25, 25), expand=True)

        img.paste(temp, (10 + i * step, random.randint(0, 15)), temp)

    for _ in range(4):
        draw.line([(random.randint(0, w), random.randint(0, h)),
                   (random.randint(0, w), random.randint(0, h))],
                  fill=tuple(random.randint(50,150) for _ in range(3)), width=2)

    for _ in range(80):
        draw.point((random.randint(0, w-1), random.randint(0, h-1)),
                   fill=tuple(random.randint(0,200) for _ in range(3)))

    img = img.filter(ImageFilter.GaussianBlur(1))

    buf = io.BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return buf

@app.route('/')
def index():
    session['captcha'] = gen_text()
    return render_template('index.html',
        message=session.pop('msg', None),
        message_type=session.pop('type', None))

@app.route('/captcha-image')
def captcha():
    text = session.get('captcha') or gen_text()
    session['captcha'] = text
    res = make_response(send_file(gen_image(text), mimetype='image/png'))
    res.headers['Cache-Control'] = 'no-store'
    return res

@app.route('/submit', methods=['POST'])
def submit():
    if request.form.get('captcha_input') == session.get('captcha'):
        session['msg'], session['type'] = 'Verified!', 'success'
    else:
        session['msg'], session['type'] = 'Wrong captcha!', 'error'
    return redirect(url_for('index'))

@app.route('/refresh')
def refresh():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)