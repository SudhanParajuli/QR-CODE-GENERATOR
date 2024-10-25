from flask import Flask, request, jsonify,render_template
from io import BytesIO
from PIL import Image
import segno
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    # Get data from the form
    data = request.form.get('data')
    fg_color = request.form.get('fg_color') or '#000000'  # Default to black
    bg_color = request.form.get('bg_color') or '#FFFFFF'  # Default to white
    size = int(request.form.get('size') or 10)  # Default size
    logo = request.files.get('logo')  # Get logo file if uploaded
    dpi = int(request.form.get('dpi') or 300)  # Default resolution

    # Validate input data
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Create the QR code
    qr = segno.make(data, error='h')  # 'h' means high error correction (about 30%)

    # Adjust colors and size
    buffer = BytesIO()
    
    # Generate the QR code with custom colors and save to buffer
    qr.save(buffer, kind='png', scale=size, dark=fg_color, light=bg_color, border=4)
    
    buffer.seek(0)
    
    # If a logo is uploaded, overlay it on the center of the QR code
    if logo:
        img = Image.open(buffer)
        img = img.convert("RGBA")
        logo_img = Image.open(logo)

        # Ensure the logo has an alpha channel (RGBA), if not, convert it
        if logo_img.mode != "RGBA":
            logo_img = logo_img.convert("RGBA")

        # Resize the logo to fit the QR code
        logo_img = logo_img.resize((img.size[0] // 5, img.size[1] // 5))

        # Calculate position for logo in the center
        logo_position = ((img.size[0] - logo_img.size[0]) // 2, (img.size[1] - logo_img.size[1]) // 2)

        # Paste the logo on the QR code without transparency mask issues
        img.paste(logo_img, logo_position, logo_img.split()[3])  # Use the alpha channel as a mask

        # Save the final image in memory (BytesIO)
        buffer = BytesIO()
        img.save(buffer, 'PNG', dpi=(dpi, dpi))
        buffer.seek(0)

    # Convert image to base64
    img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Return the base64-encoded image and a download link
    return jsonify({'img_data': img_data})

if __name__ == '__main__':
    app.run(debug=True)
