import os
import json

def generate_list_js(directory="bingo_spaces", output_file="bingoList.js"):
    """
    Generate a JavaScript file containing a list of image filenames as an array assigned to a variable.

    :param directory: The directory to scan for image files (default: 'bingo_spaces').
    :param output_file: The name of the JavaScript file to generate (default: 'availableSpaces.js').
    """
    # Validate the directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    # Collect image files
    image_files = [
        file for file in os.listdir(directory)
        if file.lower().endswith(('.png', '.jpg', '.jpeg')) and file.lower() != "center.png"
    ]

    if not image_files:
        print(f"No image files found in the directory '{directory}'.")
        return

    # Generate the JavaScript content
    js_content = f"var availableSpaces = {json.dumps(image_files, indent=4)};"

    # Write to the JavaScript file
    with open(output_file, "w") as js_file:
        js_file.write(js_content)

    print(f"JavaScript file with image list saved to '{output_file}'.")

# Usage
if __name__ == "__main__":
    generate_list_js()
