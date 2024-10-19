import fitz  # PyMuPDF
import pdfplumber
import os
from PIL import Image

def combine_images(images, output_path):
    """Combine multiple images into one."""
    if not images:
        print("No images to combine.")
        return None
    
    # Open images and find the total width and max height
    image_objects = [Image.open(image) for image in images]
    if not image_objects:
        print("Image list is empty, cannot combine.")
        return None
    
    widths, heights = zip(*(i.size for i in image_objects))
    
    # Create a new image with the combined width and total height
    total_width = max(widths)
    total_height = sum(heights)
    combined_image = Image.new('RGB', (total_width, total_height))

    # Paste images into the combined image
    y_offset = 0
    for im in image_objects:
        combined_image.paste(im, (0, y_offset))
        y_offset += im.height

    # Save the combined image
    combined_image.save(output_path)
    print(f"Combined image saved as {output_path}")

    # Close image objects
    for im in image_objects:
        im.close()

    return output_path

def should_combine_images(image_positions, max_distance=50):
    """Determine if images should be combined based on their positions."""
    if len(image_positions) < 2:
        return False  # No need to combine if there are fewer than two images
    
    # Calculate distances between consecutive images
    distances = [abs(image_positions[i + 1] - image_positions[i]) for i in range(len(image_positions) - 1)]
    # Check if all distances are below the threshold
    return all(distance <= max_distance for distance in distances)

def combine_or_keep_images(images, positions, output_dir, page_number):
    """Combine images if they are close enough, otherwise keep them separate."""
    if should_combine_images(positions):
        combined_image_path = os.path.join(output_dir, f"page_{page_number + 1}_combined_image.jpg")
        result = combine_images(images, combined_image_path)
        if result:
            for image in images:
                os.remove(image)  # Remove the small images after combining
            return [combined_image_path]
        else:
            return images  # If combining failed, keep separate
    else:
        # Keep images separate
        return images
        
def extract_images_from_page(page, output_dir, page_number):
    """Extract images from a given PDF page."""
    images = []
    image_positions = []
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        base_image = page.parent.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        image_filename = os.path.join(output_dir, f"page_{page_number + 1}_image_{img_index + 1}.{image_ext}")
        # Save image to file
        with open(image_filename, "wb") as image_file:
            image_file.write(image_bytes)
        images.append(image_filename)
        # Record the image's vertical position on the page
        image_positions.append(img[2])  # Assuming vertical position is at index 2 in the image tuple
        print(f"Extracted image: {image_filename}")
    
    # Combine or keep images based on their positions
    if images:
        final_images = combine_or_keep_images(images, image_positions, output_dir, page_number)
        return final_images
    else:
        print(f"No images found on page {page_number + 1}.")
        return []

def create_svg_from_graphics_data(graphics_data, svg_filename, page_width, page_height, min_paths=5, min_elements=3):
    """Generate SVG from lines, paths, curves, and filled shapes."""
    svg_content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_width}" height="{page_height}" viewBox="0 0 {page_width} {page_height}">'
    ]
    
    path_count = 0
    element_count = 0
    
    for item in graphics_data:
        if 'items' not in item or not item['items']:
            continue
        
        try:
            path_data = []
            if item['type'] in ['l', 'c', 'f']:  # Lines, curves, and filled shapes
                for shape in item['items']:
                    if shape[0] == 'l':  # Line
                        x0, y0 = shape[1].x, shape[1].y
                        x1, y1 = shape[2].x, shape[2].y
                        path_data.append(f"M{x0} {page_height - y0} L{x1} {page_height - y1}")
                    elif shape[0] == 'c':  # Curve (bezier or arc)
                        points = shape[1]
                        if len(points) == 4:
                            path_data.append(
                                f"M{points[0].x} {page_height - points[0].y} "
                                f"C{points[1].x} {page_height - points[1].y}, "
                                f"{points[2].x} {page_height - points[2].y}, "
                                f"{points[3].x} {page_height - points[3].y}"
                            )
                    elif shape[0] == 're':  # Rectangle
                        rect = shape[1]
                        x, y, w, h = rect.x0, rect.y0, rect.width, rect.height
                        fill_color = item.get('fill', (0, 0, 0))
                        fill_opacity = item.get('fill_opacity', 1.0)
                        svg_content.append(
                            f'<rect x="{x}" y="{page_height - y - h}" width="{w}" height="{h}" '
                            f'fill="rgb({fill_color[0] * 255}, {fill_color[1] * 255}, {fill_color[2] * 255})" '
                            f'fill-opacity="{fill_opacity}" />'
                        )
                        path_count += 1
                        element_count += 1
                # Only add path if it is not empty
                if path_data:
                    svg_content.append(f'<path d="{" ".join(path_data)}" stroke="black" fill="none" />')
                    path_count += 1
                    element_count += 1
            else:
                continue
            
        except Exception as e:
            print(f"Error processing item {item}: {e}")
    
    # Close the SVG content
    svg_content.append('</svg>')
    
    # Write the SVG content to a file only if there are enough paths and elements
    if path_count >= min_paths and element_count >= min_elements:
        with open(svg_filename, 'w') as svg_file:
            svg_file.write("\n".join(svg_content))
        print(f"SVG file '{svg_filename}' has been created with {path_count} paths and {element_count} elements.")
        return svg_filename
    else:
        print(f"No significant vector graphics found; the SVG file '{svg_filename}' will not be created.")
        return None

def extract_text_and_embed_assets(pdf_path, output_dir, start_page, end_page, images, tables, svgs):
    """Extract text from the PDF and embed references to images, tables, and SVGs."""
    content = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in range(start_page, end_page + 1):
            page = pdf.pages[page_number]
            text = page.extract_text()
            if not text:
                text = ""
            
            # Remove header content if possible
            lines = text.splitlines()
            filtered_text = "\n".join(line for line in lines if line.strip())
            
            # Add content for the current page
            content.append(filtered_text)
            
            # Embed table references
            if page_number in tables:
                for table_file in tables[page_number]:
                    content.append(f"\n{table_file}\n")
            
            # Embed image references
            if page_number in images:
                for image_file in images[page_number]:
                    content.append(f"\n{image_file}\n")
            
            # Embed SVG references
            if page_number in svgs:
                content.append(f"\n{svgs[page_number]}\n")

    # Save the combined content to a text file
    txt_filename = os.path.join(output_dir, "content.txt")
    with open(txt_filename, "w") as txt_file:
        txt_file.write("\n\n".join(content))
    print(f"Text content with embedded references saved to {txt_filename}")

def main():
    pdf_path = "/mnt/f/power/gpt/A827AV05.pdf"
    output_dir = "/mnt/f/power/gpt"
    start_page = 0
    end_page = 12

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Dictionaries to store file references
    images, tables, svgs = {}, {}, {}
    
    # Load the PDF and process pages
    document = fitz.open(pdf_path)
    for page_number in range(start_page, end_page + 1):
        page = document.load_page(page_number)
        graphics_data = page.get_drawings()
        
        # Extract images
        extracted_images = extract_images_from_page(page, output_dir, page_number)
        if extracted_images:
            images[page_number] = extracted_images
        
        # Create SVGs
        svg_filename = os.path.join(output_dir, f"page_{page_number + 1}_vector.svg")
        svg_path = create_svg_from_graphics_data(graphics_data, svg_filename, page.rect.width, page.rect.height)
        if svg_path:
            svgs[page_number] = svg_filename

    # Extract and embed text content with file references
    extract_text_and_embed_assets(pdf_path, output_dir, start_page, end_page, images, tables, svgs)
    
    document.close()

if __name__ == "__main__":
    main()
