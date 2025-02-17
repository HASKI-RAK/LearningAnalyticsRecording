import re
import fitz
import hashlib
from PIL import Image, UnidentifiedImageError
import io
import os
import csv
from natsort import natsorted
import glob

# assume 250 words per minute and just check how that aligns with the data, then see if visuals have a bigger impact than expected

# Define constants
AVERAGE_READING_SPEED = 250  # words per minute
VISUAL_COMPREHENSION_TIME = 20  # seconds per visual


# Function to estimate reading time for a slide
def estimate_reading_time(word_count, num_visuals):
    reading_time_text = word_count / AVERAGE_READING_SPEED
    comprehension_time_visuals = (num_visuals * VISUAL_COMPREHENSION_TIME) / 60
    total_time = reading_time_text + comprehension_time_visuals
    return total_time

# Function to calculate image hash for uniqueness detection
def calculate_image_hash(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        hash_md5 = hashlib.md5()
        hash_md5.update(image.tobytes())
        return hash_md5.hexdigest()
    except (OSError, UnidentifiedImageError) as e:
        print(f"Error processing image: {e}")
        return None # return nothing if image is coprrupted

# Function to analyze the entire PDF for text and image content
def analyze_pdf(pdf_path):
    try:
        document = fitz.open(pdf_path)
    except Exception as e:
        print(f"Failed to open PDF: {pdf_path} due to error: {e}")
        return 0, 0, 0, pdf_path # return zeros for images, word count and time if PDF cannot be opened
    
    seen_images = set()
    all_text = ""
    document_pages = len(document)
    time_per_page = []
    total_images = 0

    for page_number in range(len(document)):
        page = document.load_page(page_number)
        page_images = 0
        if page_number == 0:
            page_height = page.rect.height

        # Extract text from the page using fitz and accumulate it
        text = page.get_text("text")
        cleaned_page_text = text.replace('\n', ' ')
        all_text += cleaned_page_text

        # Extract and process images
        image_list = page.get_images(full=True)
        for img in image_list:
            xref = img[0]
            try:
                
                base_image = document.extract_image(xref)
                image_bytes = base_image["image"]

                image_hash = calculate_image_hash(image_bytes)

                if image_hash not in seen_images:
                    seen_images.add(image_hash)
                    page_images += 1
            except Exception as e:
                print(f"Error processing image on page {page_number +1} of {pdf_path}: {e}")
                continue #skip this image and continue with next one if it fails
        total_images += page_images
        page_word_count = len(re.findall(r'\w+', cleaned_page_text))  # Count word
        estimated_page_time_minutes = round(estimate_reading_time(page_word_count, page_images), 2)
        time_per_page.append(estimated_page_time_minutes)
        
    # Clean up the extracted text to calculate word count
    cleaned_text = all_text.replace('\n', ' ')  # Replace newlines with spaces
    word_count = len(re.findall(r'\w+', cleaned_text))  # Count words

    # Estimate reading time based on word count and images
    estimated_time_minutes = round(estimate_reading_time(word_count, total_images), 2)

    return total_images, word_count, time_per_page, document_pages, estimated_time_minutes, document.name, page_height


def generate_pdf_csv_file():
    # Example usage
    pdf_dir = "timeAnalytics/data/pdfs_WiSe_2425"
    output_csv = 'timeAnalytics/data/pdf_word_count_WiSe_2425.csv'


    with open(output_csv, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write header
        csv_writer.writerow(['Filename', 'Word Count', 'Image Count', 'Time per Page' 'Number of Pages', 'Estimated Reading Time per Page (Minutes)', 'Resolution Height'])

        # Use glob to find all PDF files recursively
        pdf_files = glob.glob(os.path.join(pdf_dir, '**/*.pdf'), recursive=True)

        # Sort PDF files naturally based on their hierarchical path
        sorted_pdf_files = natsorted(pdf_files, key=lambda x: os.path.normpath(x).split(os.sep))

        for pdf_file in sorted_pdf_files:
            relative_dir = os.path.relpath(os.path.dirname(pdf_file), pdf_dir)
            num_images, word_count, time_per_page, num_pages, estimated_time, name, height  = analyze_pdf(pdf_file)

            # Write data to CSV
            csv_writer.writerow([os.path.join(relative_dir, os.path.basename(name)), word_count, num_images, time_per_page, num_pages, f"{estimated_time:.2f}", height])

            print(f'Processed: {os.path.join(relative_dir, os.path.basename(name))}')
            print(f'Total number of unique images in {os.path.split(name)[1]}: {num_images}')
            print(f'Total estimated reading time: {estimated_time:.2f} minutes')

    print(f"Results saved to {output_csv}")

generate_pdf_csv_file()
#analyze_pdf('timeAnalytics/pdfs/04_UML/02_SW_Grobentwurf_OOA/SES_04_TZ_Tafelanschrift-2020-04-21_TAFELANSCHRIFT_112.pdf')