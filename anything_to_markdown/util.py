import base64
from io import BytesIO
import os
import io
import subprocess
import uuid

import base64

from openai import OpenAI

from markitdown import MarkItDown
from pdf2image import convert_from_bytes

import magic
import pypandoc

def process_image(system_message, user_message, api_key, base64_image=None, image_path=None):
    if base64_image is None and image_path is None:
        raise ValueError("Either base64_image or image_path must be provided")
    
    if base64_image is None:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        max_tokens=4000
    )

    return response

def vision_to_markdown(base_64_image, api_key, system_message=None, extracted_text=None):
    no_text_system_message = system_message or '''
You are tasked with converting an image of a page from a PDF report into markdown text. Please follow these guidelines:

1. **Content Inclusion:**
   - Transcribe all textual information exactly as it appears on the page.
   - Use appropriate markdown formatting (e.g., headers, bullet points, and tables) to mirror the structure of the document.

2. **Figures and Images:**
   - Identify and describe all informative figures and images (excluding icons and logos).
   - Provide detailed descriptions of these figures based on the content they convey. Do **not** include any image references or placeholders (e.g., `<img src>` tags).
   - Instead of embedding images, describe their content as accurately as possible (e.g., "![Figure 2: <detailed description of information presented in figure 2>]" or "![Image: An interior view of a modern kitchen.]").

3. **Exclusions:**
   - Do not include any external links, references to other files, or placeholders for images.
   - Ignore footer information, page numbers, icons, and logos.

4. **Clarity and Formatting:**
   - Ensure the markdown text is clean, well-organized, and mirrors the original layout of the content.
   - If any text or figure is unclear or illegible, indicate this appropriately in the markdown text.

Format your response as follows:
```markdown
<Markdown text>
```
    '''.strip()

    system_message_with_text = system_message or '''
You are tasked with converting a page from a PDF report into markdown text. You will be provided with text extracted from the page. Please use this extracted text as the basis for your transcription, ensuring accuracy and completeness. Follow these guidelines:

1. **Content Inclusion:**
   - Transcribe all textual information exactly as it appears on the page using the provided extracted text.
   - Use appropriate markdown formatting (e.g., headers, bullet points, tables) to mirror the structure of the document.

2. **Figures and Images:**
   - Identify and describe all informative figures and images (excluding icons and logos) present on the page.
   - Provide detailed descriptions of these figures based on the content they convey. Do **not** include any image references or placeholders like `<img src>` tags.
   - Instead of embedding images, describe their content accurately (e.g., "![Figure 2: Detailed description of information presented in Figure 2]" or "![Image: An interior view of a modern kitchen.]").

3. **Exclusions:**
   - Do not include any external links, references to other files, or placeholders for images.
   - Ignore footer information, page numbers, icons, and logos.

4. **Clarity and Formatting:**
   - Ensure the markdown text is clean, well-organized, and reflects the original layout of the content.
   - If any text or figure is unclear or illegible in the extracted text, indicate this appropriately in the markdown.

Format your response as follows:
```markdown
<Markdown text>
```
    '''.strip()

    user_message = '''
Please proceed with converting the image according to these guidelines.
    '''.strip()

    system_message = no_text_system_message

    if extracted_text is not None:
        user_message = f'''
Please proceed with converting the image according to these guidelines. The extracted text from the image is as follows:

{extracted_text}
        '''.strip()

        system_message = system_message_with_text

    generation = process_image(system_message, user_message, api_key, base_64_image).choices[0].message.content

    if generation.startswith('```markdown'):
        generation = generation[len('```markdown'):].strip()
    if generation.endswith('```'):
        generation = generation[:-len('```')].strip()

    return generation

def convert_with_markitdown(decoded):
    markitdown = MarkItDown()
    file_stream = BytesIO(decoded)
    result = markitdown.convert_stream(file_stream)
    return result.text_content if bool(result) and bool(result.text_content) else "Conversion failed. No content."

def convert_with_openai(decoded, api_key):
    # Generate a unique filename using UUID
    # unique_filename = f"/tmp/{uuid.uuid4()}"
    
    # # Save the uploaded file to a temporary location
    # with open(unique_filename, "wb") as f:
    #     f.write(decoded)
    
    # # Convert the uploaded file to PDF using pandoc
    # pdf_filename = f"{unique_filename}.pdf"
    # subprocess.run(["pandoc", unique_filename, "-o", pdf_filename], check=True)
    
    # # Read the converted PDF file
    # with open(pdf_filename, "rb") as f:
    #     pdf_bytes = f.read()
    
    images = convert_from_bytes(decoded)
    markdown_content = []
    for image in images:
        png_bytes = io.BytesIO()
        image.save(png_bytes, format='PNG')
        png_bytes.seek(0)
        png_base64 = base64.b64encode(png_bytes.read()).decode('utf-8')
        markdown = vision_to_markdown(png_base64, api_key)
        markdown_content.append(markdown)
    
    # Clean up temporary files
    # os.remove(unique_filename)
    # os.remove(pdf_filename)
    
    return "\n\n".join(markdown_content)

def convert_with_pypandoc(decoded):
    file_stream = BytesIO(decoded)
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file_stream.read(1024)).replace("application/", "")
    with open("/tmp/tempfile", "wb") as f:
        f.write(file_stream.read())
    output = pypandoc.convert_file("/tmp/tempfile", 'md', format=mime_type)
    os.remove("/tmp/tempfile")
    return output if output else "Conversion failed. No content."

def detect_file_type(decoded):
    mime = magic.Magic(mime=True)
    return mime.from_buffer(decoded)

def parse_contents(contents, filename, method, api_key, model):
    ext = os.path.splitext(filename)[1]
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if method == 'markitdown':
        return convert_with_markitdown(decoded)
    elif method == 'openai':
        return convert_with_openai(decoded, api_key)
    elif method == 'pypandoc':
        return convert_with_pypandoc(decoded)
    return "Unsupported method"