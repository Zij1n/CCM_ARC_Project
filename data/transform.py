import os
import json
import copy
from tqdm import tqdm
import fire

# Reuse previously defined functions for grid transformations
def flip_grid(grid, direction="vertical"):
    if not all(isinstance(row, list) for row in grid):
        raise ValueError("Input must be a list of lists")
    if direction == "vertical":
        return [row[::-1] for row in grid]
    elif direction == "horizontal":
        return grid[::-1]
    else:
        raise ValueError("Direction must be 'vertical' or 'horizontal'")

def rotate_grid(grid, angle):
    if not all(isinstance(row, list) for row in grid):
        raise ValueError("Input must be a list of lists")
    if angle == 90:
        return [list(row) for row in zip(*grid[::-1])]
    elif angle == 180:
        return [row[::-1] for row in grid[::-1]]
    elif angle == 270:
        return [list(row) for row in zip(*grid)][::-1]
    else:
        raise ValueError("Angle must be 90, 180, or 270")

def grid_iter(data):
    for section in ["train", "test"]:
        if section in data:
            for example_idx, example in enumerate(data[section]):
                for grid_type in ["input", "output"]:
                    if grid_type in example:
                        yield {
                            "section": section,
                            "example_idx": example_idx,
                            "grid_type": grid_type,
                            "grid": example[grid_type],
                        }

def transform_all_grids(data, transform, **kwargs):
    new_data = copy.deepcopy(data)
    for grid_info in grid_iter(new_data):
        section = grid_info["section"]
        example_idx = grid_info["example_idx"]
        grid_type = grid_info["grid_type"]
        new_data[section][example_idx][grid_type] = transform(grid_info["grid"], **kwargs)
    return new_data

def save_dict_to_json(data, file_name):
    try:
        with open(file_name, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        # print(f"Data successfully saved to {file_name}")
    except Exception as e:
        print(f"An error occurred while saving the dictionary: {e}")

def process_and_save_json(input_path, output_dir):
    with open(input_path, 'r') as file:
        data = json.load(file)

    os.makedirs(output_dir, exist_ok=True)

    transformations = {
        "vertical_flip": {"transform": flip_grid, "kwargs": {"direction": "vertical"}},
        "horizontal_flip": {"transform": flip_grid, "kwargs": {"direction": "horizontal"}},
        "rotate_90": {"transform": rotate_grid, "kwargs": {"angle": 90}},
        "rotate_180": {"transform": rotate_grid, "kwargs": {"angle": 180}},
        "rotate_270": {"transform": rotate_grid, "kwargs": {"angle": 270}},
    }

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    for name, params in transformations.items():
        transformed_data = transform_all_grids(data, params["transform"], **params["kwargs"])
        save_path = os.path.join(output_dir, f"{base_name}_{name}.json")
        save_dict_to_json(transformed_data, save_path)

def process_folder(folder_path):
    """
    Processes all JSON files in a folder, applies transformations, 
    and saves them in a transformed_<folder_name> directory.

    :param folder_path: Path to the folder containing JSON files.
    """
    folder_path = os.path.abspath(folder_path)
    folder_name = os.path.basename(folder_path)
    output_dir = os.path.join(os.path.dirname(folder_path), f"transformed_{folder_name}")

    os.makedirs(output_dir, exist_ok=True)

    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    if not json_files:
        print("No JSON files found in the folder.")
        return

    print(f"Processing {len(json_files)} JSON files...")
    for json_file in tqdm(json_files, desc="Processing files"):
        input_path = os.path.join(folder_path, json_file)
        process_and_save_json(input_path, output_dir)

    print(f"Transformed files saved in: {output_dir}")

if __name__ == "__main__":
    fire.Fire(process_folder)
