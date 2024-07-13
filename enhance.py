
#!/usr/bin/env python
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.misc
import math
from PIL import Image
import random
from utils import *
from models.models import *
import pytesseract
input_size = (256,256,1)

task =  sys.argv[1]
def extract_text(image_path, output_file):
    # Use pytesseract to extract text from the image
    extracted_text = pytesseract.image_to_string(image_path)
    
    # Encrypt the extracted text
    encrypted_text = encrypt_text(extracted_text)
    
    # Write the encrypted text to the output file
    with open(output_file, 'w') as file:
        file.write(encrypted_text)

def encrypt_text(text):
    encrypted_text = ""
    for char in text:
        # Skip white spaces
        if char.isspace():
            continue
        # Increment each character by 2
        encrypted_char = chr(ord(char) + 2)
        encrypted_text += encrypted_char
    return encrypted_text



if task =='binarize':
    generator = generator_model(biggest_layer=1024)
    generator.load_weights("weights/binarization_generator_weights.h5")
else:
    if task == 'deblur':
        generator = generator_model(biggest_layer=1024)
        generator.load_weights("weights/deblur_weights.h5")
    elif task == 'extracttext':
        pass
    else:
        if task =='unwatermark':
            generator = generator = generator_model(biggest_layer=512)
            generator.load_weights("weights/watermark_rem_weights.h5")
        else:
            print("Wrong task, please specify a correct task !")


if task != 'extracttext':
    deg_image_path = sys.argv[2]
    deg_image = Image.open(deg_image_path).convert('L')
    deg_image.save('curr_image.png')

    test_image = plt.imread('curr_image.png')

    h = ((test_image.shape[0] // 256) + 1) * 256
    w = ((test_image.shape[1] // 256) + 1) * 256

    test_padding = np.zeros((h, w)) + 1
    test_padding[:test_image.shape[0], :test_image.shape[1]] = test_image

    test_image_p = split2(test_padding.reshape(1, h, w, 1), 1, h, w)
    predicted_list = []
    for l in range(test_image_p.shape[0]):
        predicted_list.append(generator.predict(test_image_p[l].reshape(1, 256, 256, 1)))

    predicted_image = np.array(predicted_list)
    predicted_image = merge_image2(predicted_image, h, w)

    predicted_image = predicted_image[:test_image.shape[0], :test_image.shape[1]]
    predicted_image = predicted_image.reshape(predicted_image.shape[0], predicted_image.shape[1])

    if task == 'binarize':
        bin_thresh = 0.95
        predicted_image = (predicted_image[:, :] > bin_thresh) * 1

    output_directory = './results'
    result_image_filename = os.path.splitext(os.path.basename(deg_image_path))[0] + '.png'
    result_image_path = os.path.join(output_directory, result_image_filename)
    plt.imsave(result_image_path, predicted_image, cmap='gray')

elif task == 'extracttext':
    input_image_path = sys.argv[2]
    output_text_file = os.path.splitext(os.path.basename(input_image_path))[0] + '.txt'
    output_directory = './results'
    result_image_path = os.path.join(output_directory,output_text_file)
    extract_text(input_image_path,result_image_path)
