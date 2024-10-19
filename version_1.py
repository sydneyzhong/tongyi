import os
import fitz  # PyMuPDF

def are_lines_aligned(line1, line2, tolerance=2):
    """Check if two lines are aligned either horizontally or vertically within a tolerance."""
    x0_1, y0_1 = line1[1].x, line1[1].y
    x1_1, y1_1 = line1[2].x, line1[2].y
    x0_2, y0_2 = line2[1].x, line2[1].y
    x1_2, y1_2 = line2[2].x, line2[2].y

    horizontal_aligned = abs(y0_1 - y0_2) < tolerance and abs(y1_1 - y1_2) < tolerance
    vertical_aligned = abs(x0_1 - x0_2) < tolerance and abs(x1_1 - x1_2) < tolerance

    return horizontal_aligned or vertical_aligned

def detect_grid_pattern(lines, min_lines=3):
    """Detect if a set of lines forms a grid-like pattern."""
    horizontal_lines = [line for line in lines if abs(line[1].y - line[2].y) < 2]
    vertical_lines = [line for line in lines if abs(line[1].x - line[2].x) < 2]

    if len(horizontal_lines) >= min_lines and len(vertical_lines) >= min_lines:
        for h_line in horizontal_lines:
            aligned_with_many = sum(are_lines_aligned(h_line, other) for other in horizontal_lines) > 1
            if aligned_with_many:
                return True

        for v_line in vertical_lines:
            aligned_with_many = sum(are_lines_aligned(v_line, other) for other in vertical_lines) > 1
            if aligned_with_many:
                return True

    return False

def classify_elements(graphics_data, page_height):
    """Classify elements into vector illustrations and table wireframes based on grid patterns."""
    vector_elements = []
    table_elements = []
    
    line_items = []

    for item in graphics_data:
        if 'items' not in item or not item['items']:
            continue

        for shape in item['items']:
            if shape[0] == 'l':  # Line
                line_items.append((item, shape))

    if detect_grid_pattern([shape for _, shape in line_items]):
        for item, shape in line_items:
            table_elements.append(item)
    else:
        for item, shape in line_items:
            vector_elements.append(item)

    for item in graphics_data:
        if item not in table_elements and item not in vector_elements:
            vector_elements.append(item)

    return vector_elements, table_elements

def create_svg_from_elements(elements, svg_filename, page_width, page_height):
    """Generate SVG from given elements."""
    svg_content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page_width}" height="{page_height}" viewBox="0 0 {page_width} {page_height}">'
    ]
    
    elements_added = False
    
    for item in elements:
        path_data = []
        for shape in item['items']:
            if shape[0] == 'l':  # Line
                x0, y0 = shape[1].x, shape[1].y
                x1, y1 = shape[2].x, shape[2].y
                path_data.append(f"M{x0} {page_height - y0} L{x1} {page_height - y1}")
            elif shape[0] == 'c':  # Curve
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
                elements_added = True
            elif shape[0] in ['s', 'fs']:  # Stroke or filled stroke
                x0, y0 = shape[1].x, shape[1].y
                x1, y1 = shape[2].x, shape[2].y
                path_data.append(f"M{x0} {page_height - y0} L{x1} {page_height - y1}")
        
        if path_data:
            svg_content.append(f'<path d="{" ".join(path_data)}" stroke="black" fill="none" />')
            elements_added = True
    
    svg_content.append('</svg>')
    
    if elements_added:
        with open(svg_filename, 'w') as svg_file:
            svg_file.write("\n".join(svg_content))
        print(f"SVG file '{svg_filename}' has been created.")
    else:
        print(f"No significant elements found for '{svg_filename}'. The file will not be created.")

def main():
    pdf_path = "/mnt/f/power/gpt/A827AV05.pdf"
    output_dir = "/mnt/f/power/gpt"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    document = fitz.open(pdf_path)
    for page_number in range(document.page_count):
        page = document.load_page(page_number)
        graphics_data = page.get_drawings()

        # Classify elements
        vector_elements, table_elements = classify_elements(graphics_data, page.rect.height)
        
        # Create SVG for vector illustration
        vector_svg_filename = os.path.join(output_dir, f"page_{page_number + 1}_vector.svg")
        create_svg_from_elements(vector_elements, vector_svg_filename, page.rect.width, page.rect.height)
        
        # Create SVG for table wireframe
        table_svg_filename = os.path.join(output_dir, f"page_{page_number + 1}_table_wireframe.svg")
        create_svg_from_elements(table_elements, table_svg_filename, page.rect.width, page.rect.height)

    document.close()

if __name__ == "__main__":
    main()
