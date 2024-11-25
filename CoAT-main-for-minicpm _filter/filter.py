import json
import os
import imagesize
import shutil
from action_matching import is_tap_action
from PIL import Image, ImageDraw
from coat.screen_utils import check_inside
def highlight_elements(image_path, ui_positions, touch_point, output_path):
    # 加载图片并获取尺寸
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # 根据图片尺寸将相对位置转换为绝对位置
    for pos in ui_positions:
        ymin, xmin, rel_height, rel_width = pos
        abs_xmin = int(xmin * width)
        abs_ymin = int(ymin * height)
        abs_xmax = int((xmin + rel_width) * width)
        abs_ymax = int((ymin + rel_height) * height)

        # 用红色矩形框标出UI元素位置
        draw.rectangle([abs_xmin, abs_ymin, abs_xmax, abs_ymax], outline="red", width=2)

    # 将点击位置的相对坐标转换为绝对坐标
    touch_x = int(touch_point[1] * width)
    touch_y = int(touch_point[0] * height)

    # 用蓝色圆圈标出点击位置
    radius = 5  # 设置半径大小
    draw.ellipse([(touch_x - radius, touch_y - radius), (touch_x + radius, touch_y + radius)], fill="blue")

    # 保存修改后的图片
    image.save(output_path)
# 函数用于从一个 JSON 文件中提取数据并判断
def extract_data_from_json(file_path,directory):
    with open(file_path, 'r') as file:
        data = json.load(file)

    results = []
    correct="yes"
    for item in data:  # 假设 data 是一个字典列表
        image_path = item.get('image_path', None)
        absolute_image_path = os.path.join(directory, image_path)
        ui_positions_str = item.get('ui_positions', "[]")
        #print(ui_positions_str)
        ui_positions = json.loads(ui_positions_str)

        result_touch_yx_str = item.get('result_touch_yx', "[]")
        result_touch_yx=json.loads(result_touch_yx_str)

        result_lift_yx_str = item.get('result_lift_yx', "[]")
        result_lift_yx=json.loads(result_lift_yx_str)

        result_action_type = item.get('result_action_type', None)
        w, h = imagesize.get(absolute_image_path)
        x=result_touch_yx[1]
        y=result_touch_yx[0]
        #print(x,y)
        if(result_action_type==4) and is_tap_action(result_touch_yx,result_lift_yx):#说明是点击动作
            find="no"
            #print(ui_positions)
            for ui_position in ui_positions:
                #print(ui_position)
                ymin, xmin, h, w  = ui_position
                xmax=xmin+w
                ymax=ymin+h
                if (xmin<=x<=xmax) and (ymin<=y<=ymax):
                    find="yes"
                    #找对点击对应的box了
            if(find=="no"):
                correct="no"
                #print("该图片对应的点击动作无法找到对应的元素",image_path)
                #output_path = os.path.join(directory, 'output', os.path.basename(image_path))
                #highlight_elements(absolute_image_path, ui_positions, result_touch_yx, output_path)
                #print(x,y,ui_positions)
    if(correct=="yes"):
        #说明整个任务都是对的，保存
        parent_directory = os.path.dirname(file_path)
        target_directory = parent_directory.replace('dataset_test', 'dataset_test_filter')
        shutil.copytree(parent_directory,target_directory, dirs_exist_ok=True)
        print(f"已将包含正确 JSON 文件的目录 {parent_directory} 保存到 {target_directory}")
        # results.append({
        #     'image_path': image_path,
        #     'ui_positions': ui_positions,
        #     'result_touch_yx': result_touch_yx,
        #     "coat_action_desc": coat_action_desc
        # })

    return results

# 递归搜索目录中的所有 JSON 文件
def process_json_files(directory):
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                extracted_data = extract_data_from_json(file_path,directory)
                results.append({
                    'file': file_path,
                    'data': extracted_data
                })
    return results

# 使用示例
directory_path = '/home/test/test03/minicpm-a/model_evaluation/aitw/dataset_test/test/'  # 这里需要替换为你的目录路径
all_extracted_data = process_json_files(directory_path)
#print(all_extracted_data)