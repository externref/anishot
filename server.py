import io
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import Response
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

@app.post("/debug")
async def debug():
    return {
        "active": True,
    }

@app.post("/apply")
async def apply(file: UploadFile, addWatermark: bool = Form(False)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        if addWatermark:
            image_draw = ImageDraw.Draw(image)
            font_size = max(20, int(image.width * 0.05))
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default(font_size) 
            text = "anishot_"
            padding = int(font_size * 0.5) 
            text_width, text_height = image_draw.textbbox((0, 0), text, font=font)[2:]
            position = (image.width - text_width - padding, image.height - text_height - padding)
            image_draw.text(position, text, font=font, fill="white")

        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format="PNG")
        img_byte_array.seek(0)

        return Response(content=img_byte_array.getvalue(), media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
