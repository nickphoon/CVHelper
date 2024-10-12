import os
import argparse
from tensorflow.keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

'''
This script helps to increase the amount of data from a limited dataset
The dataset must have train and test splits.

Example usage: python dataprocessing.py fo_dataset

follow this structure:
        fo_dataset
        |__ P1
            |______ 00000128.jpg
            |______ 00000181.jpg
            |______ ...
        |__ P2
            |______ 00000243.jpg
            |______ 00000306.jpg
            |______ ...
        ...


Args:
    input_base_dir: Path to the directory of the images for augmenting data 

'''

def augment_images(input_base_dir):
    output_base_dir = f"{input_base_dir}_augmented"

    # Ensure the output base directory exists
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)

    # Data augmentation settings
    datagen = ImageDataGenerator(
        width_shift_range=0.1,  # Range for random horizontal shifts.
        height_shift_range=0.1,  # Range for random vertical shifts.
        shear_range=0.2,  # Shear intensity (shear angle in counter-clockwise direction as radians).
        zoom_range=0.1,  # Zoom range for random zoom.
        horizontal_flip=True,  # Randomly flip inputs horizontally
        fill_mode='nearest'  # Points outside the boundaries of the input are filled according to the given mode ('constant', 'nearest', 'reflect', or 'wrap').
    )

    # Walk through the base input directory
    for subdir, dirs, files in os.walk(input_base_dir):
        # Skip directories named 'P1'
        dirs[:] = [d for d in dirs if d != 'P1']
        dirs[:] = [d for d in dirs if d != 'P10']
        
        for filename in files:
            if filename.endswith(".jpg") or filename.endswith(".png"):  # Add other formats if needed
                input_subdir = os.path.relpath(subdir, input_base_dir)
                output_subdir = os.path.join(output_base_dir, input_subdir)

                # Ensure the output subdirectory exists
                if not os.path.exists(output_subdir):
                    os.makedirs(output_subdir)

                img_path = os.path.join(subdir, filename)
                img = load_img(img_path)  # Load image
                x = img_to_array(img)  # Convert image to numpy array
                x = x.reshape((1,) + x.shape)  # Reshape it to (1, height, width, channels)

                i = 0
                for batch in datagen.flow(x, batch_size=1, save_to_dir=output_subdir, save_prefix='aug', save_format='jpg'):
                    i += 1
                    if i >= 3:  # Save 3 augmented images per original image
                        break

    print(f"Data augmentation complete for {input_base_dir}.")

def main(input_base_dir):
    train_dir = os.path.join(input_base_dir, 'train')
    test_dir = os.path.join(input_base_dir, 'test')

    augment_images(train_dir)
    augment_images(test_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Data augmentation for images.')
    parser.add_argument('input_base_dir', type=str, help='Path to the base directory containing train and test folders.')

    args = parser.parse_args()
    main(args.input_base_dir)