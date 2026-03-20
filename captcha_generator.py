from captcha.image import ImageCaptcha
import random
import string
# Generate random captcha text
captcha_text = ''.join(random.choices(
    string.ascii_uppercase + string.ascii_lowercase + string.digits, k=6))

# Create captcha image
image = ImageCaptcha(width=280, height=90)

# Save captcha as PNG
image.write(captcha_text, 'captcha.png')

print("CAPTCHA image has been generated and saved as 'captcha.png'")
print("Please open the image file and enter the CAPTCHA text exactly as shown.")

attempts = 3

for i in range(attempts):
    user_input = input(f"Attempt {i+1}/{attempts} - Enter CAPTCHA: ").strip()

    # Case-sensitive comparison
    if user_input == captcha_text:
        print("✅ CAPTCHA matched! Access granted.")
        break
    else:
        print("❌ Incorrect CAPTCHA.")

        if i == attempts - 1:
            print("🚫 All attempts used. Access denied.")
            print("Original CAPTCHA was:", captcha_text)