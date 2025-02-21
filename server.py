import io

import fastapi
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import Response
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

@app.post("/apply")
async def apply(file: UploadFile, addWatermark: bool = Form(False)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        if addWatermark:
            image_draw = ImageDraw.Draw(image)
            fontface = ImageFont.load_default()
            text = "anishot_"
            text_width, text_height = image_draw.textsize(text, font=fontface)
            
            position = (image.width - text_width - 10, image.height - text_height - 10)
            image_draw.text(position, text, font=fontface)
        
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format="PNG")
        img_byte_array.seek(0)
        return Response(content=img_byte_array.getvalue(), media_type="image/png")
    except Exception as e:
        raise e
