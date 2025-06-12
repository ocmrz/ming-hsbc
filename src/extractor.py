from openai import OpenAI
from pdf2image import convert_from_path as convert_doc_to_images
import base64
import io
import os

def get_img_uri(img):
    png_buffer = io.BytesIO()
    img.save(png_buffer, format="PNG")
    png_buffer.seek(0)

    base64_png = base64.b64encode(png_buffer.read()).decode('utf-8')

    data_uri = f"data:image/png;base64,{base64_png}"
    return data_uri

client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")

imgs = convert_doc_to_images("assets/leaflet.pdf")
img_uris = [get_img_uri(img) for img in imgs]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": """You will be provided with an image of a PDF page or a slide. Your goal is to deliver detailed and engaging presentation about the content you see, using clear and accessible
language suitable for a 101-level audience.
If there is an identifiable title, start by stating the title to provide context for your audience.
Describe visual elements in detail:

Diagrams: Explain each component and how they interact. For example, "The process begins with X, which then leads to Y and results in Z."

Tables: Break down the information logically. For instance, "Product A costs X dollars, while Product B is priced at Y dollars." Focus on the content itself rather than the format:

DO NOT include terms referring to the content format.

DO NOT mention the content type. Instead, directly discuss the information presented. Keep your explanation comprehensive yet concise:

Be exhaustive in describing the content, as your audience cannot see the image.

Exclude irrelevant details such as page numbers or the position of elements on the image. Use clear and accessible language:

Explain technical terms or concepts in simple language appropriate for a 101-level audience. Engage with the content:

Interpret and analyze the information where appropriate, offering insights to help the audience understand its significance. If there is an identifiable title, present the output in the following format: (TITLE) (Content description) If there is no clear title, simply provide the content description.
"""},
    {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"{data_uri}"
                }
            } for data_uri in img_uris
        ]
    } 
])

with open("output.txt", "w") as f:
    f.write(response.choices[0].message.content or "")
