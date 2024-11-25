import os
import random
import hashlib
import shutil
from datetime import datetime
from PIL import Image, ImageDraw

import draw_bingo_init

def hash_file(file_path):
    """
    Generate the MD5 hash of a file.

    :param file_path: Path to the file to hash.
    :return: The MD5 hash as a string.
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def get_positive_integer(prompt="Enter a positive integer: "):
    """
    Prompt the user to input a positive integer. Keep reprompting until valid input is provided.

    :param prompt: The message to display when asking for input (default: "Enter a positive integer: ").
    :return: A positive integer provided by the user.
    """
    while True:
        try:
            user_input = int(input(prompt))
            if user_input > 0:
                return user_input
            else:
                print("The number must be a positive integer. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a positive integer.")

def add_white_background(image):
    """
    Ensure the image has a white background if it contains transparency.

    :param image: A PIL Image object.
    :return: A PIL Image object with a white background.
    """
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        # Create a white background
        white_bg = Image.new("RGB", image.size, (255, 255, 255))
        white_bg.paste(image, mask=image.split()[3])  # Paste using alpha channel as mask
        return white_bg
    else:
        return image.convert("RGB")  # Ensure the image is in RGB mode

def clear_directories(directories=("bingo_board", "bingo_board_with_template")):
    """
    Deletes all files inside the specified directories.

    :param directories: Tuple of directory names to clear (default: ('bingo_board', 'bingo_board_with_template')).
    """
    for directory in directories:
        if os.path.exists(directory):
            for file_name in os.listdir(directory):
                file_path = os.path.join(directory, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
            print(f"All files deleted in directory: {directory}")
        else:
            print(f"Directory not found: {directory}")

def create_bingo_matrix(
    image_folder="bingo_spaces",
    output_folder="bingo_board",
    grid_size=5,
    tile_size=(100, 100),
    center_file="center.png",
    num_cards=1
):
    """
    Create a specified number of unique bingo matrices with a fixed center image and a border around each cell.
    Save each matrix using a hash of the final image, with an additional 1px exterior border.
    Ensure no duplicate images within a single bingo board.

    :param image_folder: Folder containing PNG images (default: 'bingo_spaces').
    :param output_folder: Folder to save the bingo matrix images (default: 'bingo_board').
    :param grid_size: Size of the bingo grid (default: 5x5).
    :param tile_size: Size of each tile (default: 50x50 pixels).
    :param center_file: Filename for the fixed center image (default: 'center.png').
    :param num_cards: Number of unique bingo cards to generate (default: 1).
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Collect all PNG images in the folder except the center file
    images = [
        os.path.join(image_folder, img)
        for img in os.listdir(image_folder)
        if img.lower().endswith('.png') and img != center_file
    ]

    center_path = os.path.join(image_folder, center_file)
    if not os.path.exists(center_path):
        raise FileNotFoundError(f"Center file '{center_file}' not found in the folder.")

    if len(images) < (grid_size ** 2 - 1):
        raise ValueError("Not enough images to fill the bingo grid (excluding the center tile).")

    generated_hashes = set()
    cards_created = 0

    while cards_created < num_cards:
        # Randomly select images for the bingo grid (excluding the center piece)
        selected_images = random.sample(images, grid_size ** 2 - 1)

        # Ensure all selected images are unique within the bingo board
        selected_set = set(selected_images)  # Use a set for duplicate checks
        if len(selected_set) != len(selected_images):
            print("Duplicates detected, abandon iteration.")
            continue  # Skip this iteration if duplicates are detected

        # Create a blank canvas for the bingo matrix with borders
        canvas_size = (grid_size * (tile_size[0] + 1) - 1, grid_size * (tile_size[1] + 1) - 1)  # Include borders
        bingo_matrix = Image.new('RGB', canvas_size, "white")
        draw = ImageDraw.Draw(bingo_matrix)

        # Populate the bingo matrix with the selected images
        index = 0
        for row in range(grid_size):
            for col in range(grid_size):
                x, y = col * (tile_size[0] + 1), row * (tile_size[1] + 1)
                if row == grid_size // 2 and col == grid_size // 2:
                    # Place the center image
                    tile_image = add_white_background(Image.open(center_path).resize(tile_size))
                else:
                    # Place a random image
                    tile_path = selected_images[index]
                    tile_image = add_white_background(Image.open(tile_path).resize(tile_size))
                    index += 1
                
                # Paste the image on the canvas
                bingo_matrix.paste(tile_image, (x, y))

                # Draw a border around the cell
                draw.rectangle(
                    [x, y, x + tile_size[0], y + tile_size[1]],
                    outline="black",
                    width=1
                )

        # Add a 1px exterior border around the final image
        final_canvas_size = (canvas_size[0] + 2, canvas_size[1] + 2)  # Add 1px on all sides
        final_image = Image.new('RGB', final_canvas_size, "black")  # Black border
        final_image.paste(bingo_matrix, (1, 1))  # Paste bingo matrix with a 1px offset

        # Calculate the hash of the final image
        hash_obj = hashlib.md5()
        final_image_bytes = final_image.tobytes()
        hash_obj.update(final_image_bytes)
        image_hash = hash_obj.hexdigest()
        output_file = os.path.join(output_folder, f"bingo_{image_hash}.png")

        # Check if a file with this hash already exists or has been generated in this run
        if image_hash not in generated_hashes and not os.path.exists(output_file):
            # Save the final image with the exterior border
            final_image.save(output_file)
            print(f"Bingo matrix saved as {output_file}")
            generated_hashes.add(image_hash)
            cards_created += 1
        else:
            print(f"A bingo matrix with hash {image_hash} already exists. Regenerating...")


def generate_template(
    output_file="bingo_border_template.png",
    backup_folder="template_backups",
    template_size=(4.25, 5.5),
    dpi=300,
    grid_size=5,
    border_size=1
):
    """
    Generates a bingo template with a black box scaled to 80% of the template width.
    If the template already exists, it is moved to a backup folder with a timestamped name.
    Checks if the new template matches the hash of the existing one. Prompts the user before overwriting.

    :param output_file: The name of the file to save the template.
    :param backup_folder: Folder to store backups of existing templates.
    :param template_size: Tuple representing the template size (quarter letter sheet) in inches (default: 4.25x5.5 inches).
    :param dpi: The resolution of the image in DPI (default: 300).
    :param grid_size: The number of tiles in the grid (default: 5x5).
    :param border_size: The size of the border between tiles (default: 1 pixel).
    """
    # Check if the backup folder exists, create it if not
    os.makedirs(backup_folder, exist_ok=True)

    # Calculate template dimensions in pixels
    template_width_px = int(template_size[0] * dpi)
    template_height_px = int(template_size[1] * dpi)

    # Calculate the scaled board dimensions (80% of template width)
    scaled_board_width = int(template_width_px * 0.8)
    scaled_board_height = scaled_board_width  # Square grid

    # Create a new image with the specified background color
    template = Image.new("RGB", (template_width_px, template_height_px), (100, 100, 100))
    draw = ImageDraw.Draw(template)

    # Calculate the position of the black box to center it horizontally and align with bottom margin
    left_margin = (template_width_px - scaled_board_width) // 2
    bottom_margin = left_margin
    x0 = left_margin
    y0 = template_height_px - bottom_margin - scaled_board_height
    x1 = x0 + scaled_board_width
    y1 = y0 + scaled_board_height

    # Draw the black box
    draw.rectangle([x0, y0, x1, y1], fill="black")

    # Save the template temporarily
    temp_output = f"temp_{output_file}"
    template.save(temp_output)

    # Check the hash of the newly generated template
    new_template_hash = hash_file(temp_output)
    print(f"Generated Template Hash: {new_template_hash}")

    existing_template_hash = None
    if os.path.exists(output_file):
        # Generate a hash of the existing file
        existing_template_hash = hash_file(output_file)
        print(f"Existing Template Hash:  {existing_template_hash}")

    if existing_template_hash and new_template_hash != existing_template_hash:
        confirm = input("The newly generated template does not match the existing template. Do you want to overwrite the existing edited template? (yes/no): ").strip().lower()
        if confirm[0] != "y":
            os.remove(temp_output)  # Remove the temporary file if not overwriting
            print("Template generation canceled.")
            return
    elif existing_template_hash and new_template_hash == existing_template_hash:
        print("Default template already generated.")
        return
    else:
        if os.path.exists(output_file):
            # Generate a timestamp for the backup file
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
            backup_file = os.path.join(backup_folder, f"bingo_border_template_{timestamp}.png")
            # Move the existing file to the backup folder
            shutil.move(output_file, backup_file)
            print(f"Existing template moved to backup: {backup_file}")

    # Move the new template to the final location
    shutil.move(temp_output, output_file)
    print(f"Board template saved as {output_file}")


def merge_with_template(input_folder="bingo_board", output_folder="bingo_board_with_template", template_file="bingo_border_template.png"):
    """
    Merge all .png images in the input folder with a template scaled to 80% of the width of the template,
    and save the results in the output folder.

    :param input_folder: Folder containing bingo board images (default: 'bingo_board').
    :param output_folder: Folder to save merged images (default: 'bingo_board_with_template').
    :param template_file: Template file with a transparent section for the board.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Load the template image or generate it if not found
    try:
        template = Image.open(template_file).convert("RGBA")
    except FileNotFoundError:
        print(f"Template file '{template_file}' not found. Generating a new template...")
        generate_template(output_file=template_file)
        print(f"Template '{template_file}' generated. Please review and edit it as needed.")
        return

    # Prompt the user to finalize the template
    print("There is a new file named 'bingo_border_template.png'. Edit it, make a copy of it somewhere else, then proceed with the prompt below.")
    confirm = input("Have you finalized editing the template? (yes/no): ").strip().lower()
    if confirm[0] != "y":
        print("Please edit the template and run this function again.")
        return

    # Get the dimensions of the template
    template_width, template_height = template.size

    # Scale dimensions for the board (80% of template width)
    scaled_board_width = int(template_width * 0.8)
    scaled_board_height = scaled_board_width  # Square grid

    # Process each .png file in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(".png"):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, file_name)

            # Open the bingo board image
            bingo_board = Image.open(input_path).convert("RGBA")

            # Resize the bingo board to fit the scaled dimensions
            bingo_board_resized = bingo_board.resize((scaled_board_width, scaled_board_height))

            # Calculate the position to align the bingo board
            left_margin = (template_width - scaled_board_width) // 2
            bottom_margin = left_margin
            x_offset = left_margin
            y_offset = template_height - scaled_board_height - bottom_margin

            # Create a copy of the template to overlay the bingo board
            merged_image = template.copy()
            merged_image.paste(bingo_board_resized, (x_offset, y_offset), bingo_board_resized)

            # Save the merged image
            merged_image.save(output_path)
            print(f"Merged template saved as {output_path}")

def images_to_pdf(input_folder="bingo_board_with_template", output_file="bingo_cards.pdf"):
    """
    Convert all images in the specified folder into a multipage PDF.

    :param input_folder: Folder containing the images to convert (default: 'bingo_board_with_template').
    :param output_file: Output file name for the PDF (default: 'bingo_cards.pdf').
    """
    # Collect all image files from the folder
    image_files = [
        os.path.join(input_folder, file_name)
        for file_name in sorted(os.listdir(input_folder))
        if file_name.lower().endswith('.png')
    ]

    if not image_files:
        print("No images found in the folder. Please check the input folder.")
        return

    # Open all images and ensure they are in RGB mode
    images = [Image.open(img).convert("RGB") for img in image_files]

    # Use the first image as the base and append the rest
    base_image = images[0]
    additional_images = images[1:]

    while True:
        try:
            # Save as a multipage PDF
            base_image.save(output_file, save_all=True, append_images=additional_images)
            print(f"PDF created successfully: {output_file}")
            print("Remember to print in 2x2 configuration!")
            print(f"There should be {len(image_files)//4} pages to print.")
            break  # Exit the loop if saving is successful
        except PermissionError:
            input(
                f"Permission error: Unable to save the file '{output_file}'. "
                "Please close the file if it is open and press Enter to retry."
            )


# Usage example
if __name__ == "__main__":

    draw_bingo_init.generate_list_js()

    num_cards = get_positive_integer("Enter the number of unique bingo cards to generate: ")
    
    # For quarter sheets, multiples of 4 are p
    if num_cards % 4 != 0:
        num_cards = ((num_cards // 4) + 1) * 4
        print(f"Filling out a page with quarter sheets... Generating {num_cards} bingo cards.")

    clear_directories()
    create_bingo_matrix(num_cards=num_cards)
    generate_template()
    merge_with_template()
    images_to_pdf()