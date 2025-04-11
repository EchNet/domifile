# pdf_to_image.py

import sys
import os
from pdf2image import convert_from_path
from PIL import Image
from errors import ApplicationError


def pdf_to_image(pdf_path):
  """
    Convert PDF to image.  Requires poppler.
  """
  images = convert_from_path(pdf_path, dpi=300)
  if not images:
    raise ApplicationError("Error: No images extracted from PDF.")

  # Get total width (max width of all pages) and total height (sum of heights)
  total_width = max(img.width for img in images)
  total_height = sum(img.height for img in images)

  # Create blank image
  merged_image = Image.new("RGB", (total_width, total_height))

  # Paste each image one below the other
  y_offset = 0
  for img in images:
    merged_image.paste(img, (0, y_offset))
    y_offset += img.height

  # Save the merged image
  output_path = os.path.splitext(pdf_path)[0] + ".png"  # Replace .pdf with .png
  merged_image.save(output_path, "PNG")
  return output_path
