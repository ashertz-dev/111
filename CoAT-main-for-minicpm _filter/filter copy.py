import json
import os
import imagesize
import shutil
from action_matching import is_tap_action
from PIL import Image, ImageDraw
from coat.screen_utils import check_inside

def highlight_elements(image_path, ui_positions, touch_point, output_path):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    width, height = image.size

    for pos in ui_positions:
        ymin, xmin, rel_height, rel_width = pos
        abs_xmin = int(xmin * width)
        abs_ymin = int(ymin * height)
        abs_xmax = int((xmin + rel_width) * width)
        abs_ymax = int((ymin + rel_height) * height)
        draw.rectangle([abs_xmin, abs_ymin, abs_xmax, abs_ymax], outline="red", width=2)

    touch_x = int(touch_point[1] * width)
    touch_y = int(touch_point[0] * height)
    radius = 5
    draw.ellipse([(touch_x - radius, touch_y - radius), (touch_x + radius, touch_y + radius)], fill="blue")
    image.save(output_path)

def extract_data_from_json(file_path, directory, saved_dirs):
    with open(file_path, 'r') as file:
        data = json.load(file)

    results = []
    correct = "yes"
    for item in data:
        image_path = item.get('image_path', None)
        absolute_image_path = os.path.join(directory, image_path)
        ui_positions = json.loads(item.get('ui_positions', "[]"))
        result_touch_yx = json.loads(item.get('result_touch_yx', "[]"))
        result_lift_yx = json.loads(item.get('result_lift_yx', "[]"))
        result_action_type = item.get('result_action_type', None)
        x=result_touch_yx[1]
        y=result_touch_yx[0]
        if result_action_type == 4 and is_tap_action(result_touch_yx, result_lift_yx):
            find = "no"
            for ui_position in ui_positions:
                ymin, xmin, h, w = ui_position
                xmax = xmin + w
                ymax = ymin + h
                if xmin <= x <= xmax and ymin <= y <= ymax:
                    find = "yes"
            if find == "no":
                correct = "no"
                output_path = os.path.join("/home/test/test03/minicpm-a/model_evaluation/aitz/CoAT-main_kun/", 'output', os.path.basename(image_path) + '.png')
                highlight_elements(absolute_image_path, ui_positions, result_touch_yx, output_path)

    if correct == "yes":
        parent_directory = os.path.dirname(file_path)
        target_directory = parent_directory.replace('dataset_test', 'dataset_test_filter')
        if saved_dirs.get(target_directory, 0) < 100:
            shutil.copytree(parent_directory, target_directory, dirs_exist_ok=True)
            saved_dirs[target_directory] = saved_dirs.get(target_directory, 0) + 1
            print(f"已将包含正确 JSON 文件的目录 {parent_directory} 保存到 {target_directory}")

    return results

def process_json_files(directory):
    saved_dirs = {}
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                extracted_data = extract_data_from_json(file_path, directory, saved_dirs)
                results.append({'file': file_path, 'data': extracted_data})
    return results

directory_path = '/home/test/test03/minicpm-a/model_evaluation/aitw/dataset_test/test/'
all_extracted_data = process_json_files(directory_path)
