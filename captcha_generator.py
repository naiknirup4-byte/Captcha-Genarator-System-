from captcha.image import ImageCaptcha
import random
import string

# Generate random captcha text
captcha_text = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase+ string.digits, k=6))

# Create captcha image
image = ImageCaptcha(width=280, height=90)

# Save captcha as PNG
image.write(captcha_text, 'captcha.png')

print("Captcha text:", captcha_text)
print("Captcha image saved as captcha.png")