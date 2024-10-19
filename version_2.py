import fitz  # PyMuPDF
import pdfplumber
import os

def extract_images_from_page(page, output_dir, page_number):
    """Extracts images from a given PDF page."""
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        base_image = page.parent.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        image_filename = os.path.join(output_dir, f"page_{page_number + 1}_image_{img_index + 1}.{image_ext}")
        # Save image to file
        with open(image_filename, "wb") as image_file:
            image_file.write(image_bytes)
        print(f"Extracted image: {image_filename}")

def create_svg_from_graphics_data(graphics_data, svg_filename, page_width, page_height):
    """Generate SVG from lines, paths, curves, and filled shapes."""
    svg_content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_width}" height="{page_height}" viewBox="0 0 {page_width} {page_height}">'
    ]
    
    # Track whether we add any meaningful paths
    paths_added = False
    
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
                        paths_added = True
                # Only add path if it is not empty
                if path_data:
                    paths_added = True
                    svg_content.append(f'<path d="{" ".join(path_data)}" stroke="black" fill="none" />')
            else:
                # Skip unsupported types
                continue
            
        except Exception as e:
            print(f"Error processing item {item}: {e}")
    
    # Close the SVG content
    svg_content.append('</svg>')
    
    # Write the SVG content to a file only if paths were added
    if paths_added:
        with open(svg_filename, 'w') as svg_file:
            svg_file.write("\n".join(svg_content))
        print(f"SVG file '{svg_filename}' has been created.")
    else:
        print(f"No valid vector graphics found; the SVG file '{svg_filename}' will not be created.")

def extract_tables(pdf_path, output_dir, start_page, end_page):
    """Extract tables from a range of pages and combine multi-page tables."""
    combined_table = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in range(start_page, end_page + 1):
            page = pdf.pages[page_number]
            tables = page.extract_tables()
            if not tables:
                print(f"No tables found on page {page_number + 1}.")
                continue
            for table in tables:
                # If the table is a continuation of a previous table, merge it
                if combined_table and len(combined_table[-1]) > 0 and len(table) > 0:
                    combined_table.extend(table[1:])  # Skip header row
                else:
                    combined_table.extend(table)

        # Save the combined table to a CSV file if it is not empty
        if combined_table:
            csv_filename = os.path.join(output_dir, f'combined_table_{start_page + 1}_to_{end_page + 1}.csv')
            with open(csv_filename, 'w') as csv_file:
                for row in combined_table:
                    merged_row = [str(cell).replace("\n", " ") if cell is not None else "" for cell in row]
                    csv_file.write(",".join(merged_row) + "\n")
            print(f"Combined table saved to {csv_filename}")
        else:
            print(f"No combined table data found for pages {start_page + 1} to {end_page + 1}.")

def main():
    pdf_path = "/mnt/f/power/gpt/A827AV05.pdf"
    output_dir = "/mnt/f/power/gpt"
    start_page = 0  # Page index starts from 0
    end_page = 12    # Last page index to include in table extraction

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load the PDF and extract images and graphics data
    document = fitz.open(pdf_path)
    for page_number in range(start_page, end_page + 1):
        page = document.load_page(page_number)
        graphics_data = page.get_drawings()
        
        # Extract images from the page
        extract_images_from_page(page, output_dir, page_number)
        
        # Create SVG from the graphics data
        output_svg = os.path.join(output_dir, f"page_{page_number + 1}_vector.svg")
        create_svg_from_graphics_data(graphics_data, output_svg, page.rect.width, page.rect.height)
    
    # Extract and combine tables across multiple pages
    extract_tables(pdf_path, output_dir, start_page, end_page)
    
    document.close()

if __name__ == "__main__":
    main()
