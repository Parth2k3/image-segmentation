from django.shortcuts import render, redirect
from .forms import ImageUploadForm
from .models import UploadedImage
import cv2
import numpy as np
import pytesseract
import os
from django.conf import settings

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('display_images')
    else:
        media_directory = os.path.join(settings.MEDIA_ROOT, 'images')
    
        # Iterate over all files in the directory and delete them
        for filename in os.listdir(media_directory):
            file_path = os.path.join(media_directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})

def extract_text_and_shape(image_path):
    # Load the image
    image = cv2.imread(image_path)
    
    # Check if the image was loaded successfully
    if image is None:
        print(f"Error: Unable to load image at {image_path}")
        return None, None
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to extract text
    text = pytesseract.image_to_string(gray)

    # Thresholding to create a binary image
    _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter out small contours and find the largest one
    min_contour_area = 1000  # You may need to adjust this value
    largest_contour = None
    largest_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_contour_area and area > largest_area:
            largest_contour = contour
            largest_area = area

    # If no contour is large enough, return
    if largest_contour is None:
        print("No large contour found")
        return text, None

    # Create a mask to isolate the largest contour
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)

    # Extract the shape from the image using the mask
    shape_image = cv2.bitwise_and(image, image, mask=mask)

    # Crop the image to the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    cropped_shape_image = shape_image[y:y+h, x:x+w]

    # Save the cropped shape image
    shape_image_path = os.path.join(os.path.dirname(image_path), os.path.basename(image_path).replace('.jpg', '_shape.jpg'))
    cv2.imwrite(shape_image_path, cropped_shape_image)

    return text, shape_image_path

def display_images(request):
    images = UploadedImage.objects.all()
    image_texts_shapes = []
    processed_images = set()

    for image in images:
        if image.image.path not in processed_images:
            text, shape_image_path = extract_text_and_shape(image.image.path)
            if text is not None and shape_image_path is not None:
                shape_image_url = os.path.join(settings.MEDIA_URL, 'images', os.path.basename(shape_image_path))
                image_texts_shapes.append((text, image.image.url, shape_image_url))
            
            # Add the image path to the processed set
            processed_images.add(image.image.path)

    return render(request, 'display.html', {'image_texts_shapes': image_texts_shapes})
