import io

import fastapi
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from PIL import Image, ImageDraw, ImageFont

app = fastapi.FastAPI()


@app.post("/apply")
async def apply(file: UploadFile):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        image_draw = ImageDraw.Draw(image)
        fontface = ImageFont.load_default()
        image_draw.text((10, 10), "anishot_", font=fontface)
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format="PNG")
        img_byte_array.seek(0)
        return Response(content=img_byte_array.getvalue(), media_type="image/png")
    except Exception as e:
        raise e
