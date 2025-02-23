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

frames = {
    "kuromi": "extension/assets/kuromi.png"
}

@app.post("/apply")
async def apply(file: UploadFile, addWatermark: bool = Form(False), frame: str = Form("default")):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        if addWatermark:
            image_draw = ImageDraw.Draw(image)
            font_size = int(image.width * 0.02) 
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default(font_size)
            text = "anishot_"
            padding = int(font_size * 0.5)
            text_width, text_height = image_draw.textbbox((0, 0), text, font=font)[2:]
            position = (image.width - text_width - padding, image.height - text_height - padding)
            shadow_offset = int(font_size * 0.1)
            shadow_position = (position[0] + shadow_offset, position[1] + shadow_offset)
            image_draw.text(shadow_position, text, font=font, fill="black") 
            image_draw.text(position, text, font=font, fill="white")
        
        if frame != "default":
            frame_img = Image.open(frames[frame]).convert("RGBA")
            frame_width, frame_height = frame_img.size
            image_aspect = image.width / image.height
            frame_aspect = frame_width / frame_height
            
            if image_aspect > frame_aspect:
                new_height = frame_height
                new_width = int(frame_height * image_aspect)
            else:
                new_width = frame_width
                new_height = int(frame_width / image_aspect)
            
            image = image.resize((new_width, new_height), Image.LANCZOS)
            crop_x = (new_width - frame_width) // 2
            crop_y = (new_height - frame_height) // 2
            image = image.crop((crop_x, crop_y, crop_x + frame_width, crop_y + frame_height))
            
            image = Image.alpha_composite(image, frame_img)
        
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format="PNG")
        img_byte_array.seek(0)

        return Response(content=img_byte_array.getvalue(), media_type="image/png")

    except Exception as e:
        return {"error": str(e)}