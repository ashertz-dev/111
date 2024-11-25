import os
import re
import json
import imagesize
import numpy as np
import pandas as pd
import Levenshtein
from collections import defaultdict
from .screen_utils import row_col_sort, enlarge_bbox, check_inside, intersect_iou
import math
from PIL import Image, ImageDraw, ImageFont
from action_matching import is_tap_action
from PIL import Image, ImageDraw, ImageFont
import os
import imagesize

def annotate_and_save_image(img_path, output_folder, gt_action_type, gt_action_detail, pd_action_type, pd_action_detail, type_match, exact_match, subset, episode_id, step_id):
    """在指定文件夹中保存带有操作详情的注释图像。"""
    # 加载图像并获取尺寸
    image = Image.open(img_path)
    draw = ImageDraw.Draw(image)
    font_path = "/usr/share/fonts/dejavu/DejaVuSans.ttf"  # 根据你的系统调整路径
    font = ImageFont.truetype(font_path, 20)  # 根据需要选择更大的字体尺寸
    
    w, h = imagesize.get(img_path)

    # 创建注释文本
    annotation_text = (
        f"taskID: {subset}{episode_id}_{step_id}\n"
        f"GT action: {gt_action_type}\n"
        f"GT detail: {gt_action_detail}\n"
        f"PD action: {pd_action_type}\n"
        f"PD detail: {pd_action_detail}\n"
        f"type_match: {'Yes' if type_match else 'No'}\n"
        f"exac_match: {'Yes' if exact_match else 'No'}"
    )

    # 计算文本大小并在必要时换行
    max_width = w - 20  # 文本的最大宽度
    lines = []
    for line in annotation_text.split('\n'):
        # 按单词分割行以检查宽度
        words = line.split()
        current_line = ""
        for word in words:
            # 添加一个单词后检查宽度
            test_line = current_line + " " + word if current_line else word
            if draw.textsize(test_line, font=font)[0] > max_width:
                # 如果行太长，开始新的一行
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        lines.append(current_line)  # 添加最后形成的行

    # 在图像上绘制每一行
    y_text = 10
    for line in lines:
        draw.text((10, y_text), line, font=font, fill='red')
        y_text += draw.textsize(line, font=font)[1] + 5  # 移动到下一行的位置
    if pd_action_type == 'click' and type_match:
        ymin, xmin, height, width = gt_action_detail  # 解析GT动作细节
        pd_x = pd_action_detail["x"]*w
        pd_y =pd_action_detail["y"]*h
        gt_box = [xmin*w, ymin*h, (xmin + width)*w, (ymin + height)*h]
        draw.rectangle(gt_box, outline="green", width=3)
        point_radius = 5
        draw.ellipse((pd_x - point_radius, pd_y - point_radius, pd_x + point_radius, pd_y + point_radius), fill="blue", outline="blue")
    # 将注释图像保存到输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_file_name = os.path.basename(img_path).replace('.png', '_annotated.png')
    output_path = os.path.join(output_folder, output_file_name)
    image.save(output_path)

    return output_path

def find_closest_box(point, ui_positions):
    """
    Finds the closest box to the given point among a list of boxes.

    Parameters:
    - point (list): The [y, x] coordinates of the point.
    - ui_positions (list of lists): Each sublist represents a box with
      format [ymin, xmin, height, width].

    Returns:
    - list: The closest box to the point, or None if no box contains the point.
    """
    point_y, point_x = point
    min_distance_sum = float('inf')
    closest_box = [0,0,0,0]
    print(ui_positions)
    for box in ui_positions:
        ymin, xmin, height, width = box
        ymax = ymin + height
        xmax = xmin + width

        # Check if the point is inside the box
        if ymin <= point_y <= ymax and xmin <= point_x <= xmax:
            # Calculate the sum of distances to all four sides
            distance_sum = (point_y - ymin) + (ymax - point_y) + (point_x - xmin) + (xmax - point_x)

            # Update the closest box if this box is closer
            if distance_sum < min_distance_sum:
                min_distance_sum = distance_sum
                closest_box = box

    return closest_box



def get_direction(point1, point2):
    # 两点的坐标
    x1, y1 = point1["x"], point1["y"]
    x2, y2 = point2["x"], point2["y"]

    # 计算向量
    vector = (x2 - x1, y2 - y1)
    vx, vy = vector

    # 方向向量定义
    directions = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0)
    }

    # 归一化目标向量
    vector_length = math.sqrt(vx ** 2 + vy ** 2)
    if vector_length == 0:  # 两点相同，无法确定方向
        return "no direction"
    unit_vector = (vx / vector_length, vy / vector_length)

    # 计算与每个方向的余弦值
    max_cosine = -float('inf')
    closest_direction = None
    for direction, dir_vector in directions.items():
        dx, dy = dir_vector
        dir_length = math.sqrt(dx ** 2 + dy ** 2)
        cos_theta = (unit_vector[0] * dx + unit_vector[1] * dy) / dir_length
        if cos_theta > max_cosine:
            max_cosine = cos_theta
            closest_direction = direction

    return closest_direction


class ActionEvaluator(object):
    BBOX_PATTERN = re.compile(r'\[ *(\d+) *, *(\d+) *, *(\d+) *, *(\d+) *\]')

    def __init__(self, demo_mode, screen_mode) -> None:
        self.demo_mode = demo_mode
        self.screen_mode = screen_mode

        self._all_action_types_ = ["click", "scroll", "type", "press", "stop"]

    def action_map(self, action_api: str):
        if not action_api: return "stop"
        action_api = action_api.lower()
        if action_api == "input": return "type"
        if "point" in action_api: return "click"
        if "press" in action_api: return "press"
        if "type" in action_api: return "type"
        if "swipe" in action_api: return "scroll"
        return "stop"
        #for act_type in self._all_action_types_:
        #    if act_type in action_api: return act_type
        #return None
    def action_map_old(self, action_api: str):
        if not action_api: return None
        action_api = action_api.lower()
        if action_api == "input": return "type"
        for act_type in self._all_action_types_:
            if act_type in action_api: return act_type
        return None

    def _parse_action_(self, pred, w, h):
        pr = pred.get('action_predict', {})
        if self.demo_mode not in pr: return (None, ) * 6

        action = pr[self.demo_mode].get(self.screen_mode, {})
        if not action: return (None, ) * 6

        pd_action_type = self.action_map(action.get('ACTION', None))
        if pd_action_type is None: print(action)

        pd_action_args = action.get('ARGS', {})
        if not isinstance(pd_action_args, dict): pd_action_args = {}
        #这里要改
        x = ((pd_action_args.get('coordinate', {})).get('x', 0)) / 1000
        y = ((pd_action_args.get('coordinate', {})).get('y', 0)) / 1000
        pd_action_xy = {"x": x, "y": y}
        # if x is not None and y is not None:
        #     # xmin = round(0/1000 * w)
        #     # ymin = round(0/1000 * h)
        #     # xmax = round(1000/1000 * w)
        #     # ymax = round(1000/1000 * h)
        #     xmin = round((x-70)/1000 * w)
        #     ymin = round((y-70)/1000 * h)
        #     xmax = round((x+70)/1000 * w)
        #     ymax = round((y+70)/1000 * h)
        # pd_action_bbox = pd_action_args.get('bbox', None)
        # if pd_action_bbox is not None:
        #     xmin, ymin, xmax, ymax = pd_action_bbox[:4]
        #     xmin = round(xmin/1000 * w)
        #     ymin = round(ymin/1000 * h)
        #     xmax = round(xmax/1000 * w)
        #     ymax = round(ymax/1000 * h)
        # pd_action_bbox = [xmin, ymin, xmax, ymax]
        # print(pd_action_bbox)

        pd_action_idx = pd_action_args.get('idx', None)
        if pd_action_idx:
            try:
                pd_action_idx = int(pd_action_idx)
            except:
                pd_action_idx = None
        #这个要加判断
        point1 = pd_action_args.get('touch_coordinate', None)
        point2 = pd_action_args.get('lift_coordinate', None)
        #pd_action_direction = pd_action_args.get('direction', None)
        pd_action_direction = None
        if point1 is not None and point2 is not None:
            pd_action_direction = get_direction(point1, point2)
        pd_action_text = pd_action_args.get('text', "")
        pd_action_button = None if pd_action_type != "press" else \
            (pd_action_args.get("button")).lower()

        return pd_action_type, pd_action_xy, pd_action_idx, \
               pd_action_direction, pd_action_text, pd_action_button

    def _parse_answer_(self, gt):
        gt_cand_nodes=None
        gt_action_text=None
        gt_action_type=None
        gt_action_xy=None
        gt_action_direction=None
        gt_action_button=None
        if gt['result_action_type'] == 3:
            gt_action_type = "type"
            gt_action_text = gt['result_action_text']
        if gt['result_action_type'] == 4:  #可能是滑动或者点击
            normalized_start_yx = gt['result_touch_yx']
            normalized_start_yx = json.loads(normalized_start_yx)
            normalized_end_yx = gt['result_lift_yx']
            normalized_end_yx =json.loads(normalized_end_yx)
            if is_tap_action(normalized_start_yx, normalized_end_yx):
                ui_positions = json.loads(gt['ui_positions'])
                gt_action_type = "click"
                gt_cand_nodes = find_closest_box(normalized_start_yx,
                                                 ui_positions)
            else:
                point1 = {
                    "y": normalized_start_yx[0],
                    "x": normalized_start_yx[1]
                }
                point2 = {"y": normalized_end_yx[0], "x": normalized_end_yx[1]}
                gt_action_type = "scroll"
                gt_action_direction = get_direction(point1, point2)
        if gt['result_action_type'] == 5:
            gt_action_type = "press"
            gt_action_button = "back"
        if gt['result_action_type'] == 6:
            gt_action_type = "press"
            gt_action_button = "home"
        if gt['result_action_type'] == 7:
            gt_action_type = "press"
            gt_action_button = "enter"
        if gt['result_action_type'] == 10 or gt['result_action_type'] == 11:
            gt_action_type = "stop"
            gt_action_text = gt['result_action_text']
        #这里实际上用不上gt_action_xy了，但是为了保持代码结构没有去掉
        gt_action_xy = []
        # gt_words = gt['coat_action_desc'].split(' ')

        # gt_action_type = self.action_map_old(gt_words[0])
        # #gt_action_type = self.action_map(gt_words)
        # if gt_action_type is None: print(gt['subset'], gt['episode_id'])
        # gt_action_text = gt['result_action_text']
        # gt_action_direction = "" if gt_action_type != "scroll" else gt_words[1].strip()
        # gt_action_button = ""
        # if gt_action_type == "press":
        #     for button in ['enter', 'back', 'home']:
        #         if button in gt['coat_action_desc']:
        #             gt_action_button = button
        #             break

        # w, h = imagesize.get(gt['image_full_path'])
        # gt_action_xy = [0, 0]
        # #这里是我(付屹堃）改的，因为实在好奇怪
        # #这样说明是滑动
        # if gt_action_type == "scroll" and (gt_action_direction == "up" or gt_action_direction == "down" or gt_action_direction == "right" or gt_action_direction == "left"):
        #     print("hi，哥们是纯正滑动")
        # elif gt_action_type == "scroll":
        #     print("这样说明其实是click")
        #     rel_y, rel_x = json.loads(gt['result_touch_yx'])
        #     abs_y, abs_x = int(rel_y*h), int(rel_x*w)
        #     gt_action_xy = [abs_x, abs_y]
        #     gt_action_type = "click"
        # if gt_action_type == "click":
        #     print("纯正click")
        #     rel_y, rel_x = json.loads(gt['result_touch_yx'])
        #     abs_y, abs_x = int(rel_y*h), int(rel_x*w)
        #     gt_action_xy = [abs_x, abs_y]
        #     gt_action_type = "click"

        # gt_cand_nodes = []
        # for org_bbox, txt, ui_class in zip(gt['ui_positions'], gt['ui_text'], gt['ui_types']):
        #     ymin, xmin, h, w  = org_bbox
        #     bbox = [xmin, ymin, xmin+w, ymin+h]
        #     gt_cand_nodes.append({"bounds": bbox, "text": txt, "type": ui_class})
        # gt_cand_nodes = row_col_sort(gt_cand_nodes)

        return gt_action_type, gt_action_xy, gt_cand_nodes, \
               gt_action_text, gt_action_button, gt_action_direction

    def _check_click_(self, pred_bbox, gt_xy, gt_nodes):
        # gt_xy is within pred_bbox
        if not pred_bbox: return False
        pred_bbox = enlarge_bbox([pred_bbox])[0]
        xmin, ymin, xmax, ymax = pred_bbox
        gt_x, gt_y = gt_xy
        is_correct = (xmin <= gt_x <= xmax and ymin <= gt_y <= ymax)
        if is_correct: return True

        # gt_xy is within any bbox
        bbox_array = enlarge_bbox([x['bounds'] for x in gt_nodes],
                                  scale_factor=1.2)
        is_inside, bbox_inside = check_inside(gt_x, gt_y, bbox_array)
        if is_inside:
            ious = intersect_iou(pred_bbox, bbox_inside)
            if np.any(ious > 0.5): return True

        return False

    def __call__(self, gt, pred):
        """ eval_single_step """
        pd_action_detail = None

        subset, episode_id, step_id = gt['subset'], gt['episode_id'], gt[
            'step_id']
        w, h = imagesize.get(gt['image_full_path'])

        # get ground truth information
        gt_action_type, gt_action_xy, gt_cand_nodes, \
            gt_action_text, gt_action_button, gt_action_direction = self._parse_answer_(gt)
        if not gt_action_type: print(gt['result_action_type'])
        gt_action_detail = {
            "click": gt_cand_nodes,
            "scroll": gt_action_direction,
            "type": gt_action_text,
            "press": gt_action_button,
            "stop": "stop"
        }.get(gt_action_type, None)

        # get predict action information
        pd_action_type, pd_action_xy, pd_action_idx, \
            pd_action_direction, pd_action_text, pd_action_button = self._parse_action_(pred, w, h)
        print("预测动作", pd_action_type)
        print("实际动作", gt_action_type)
        # compute metrics
        hit_format = True if pd_action_type is not None else False
        type_match = (pd_action_type is not None
                      and gt_action_type == pd_action_type)
        pd_action_detail={
            "click": pd_action_xy,
            "scroll": pd_action_direction,
            "type": pd_action_text,
            "press": pd_action_button,
            "stop": "stop"
        }.get(pd_action_type, None)
        exact_match = False
        text_dist = None
        if type_match and pd_action_type == "click":
            #print("hihi")
            # if self.screen_mode == "tag" and pd_action_idx: # transform idx into bbox
            #     if 0 <= pd_action_idx < len(gt_cand_nodes):
            #         pd_action_bbox = gt_cand_nodes[pd_action_idx]['bounds']
            pd_action_detail = pd_action_xy
            ymin, xmin, height, width = gt_cand_nodes
            ymax = ymin + height
            xmax = xmin + width
            exact_match = ((ymin <= pd_action_xy["y"] <= ymax)
                           and (xmin <= pd_action_xy["x"] <= xmax))
            #exact_match = self._check_click_(pd_action_bbox, gt_action_xy, gt_cand_nodes)

        if type_match and pd_action_type == "scroll":
            pd_action_detail = pd_action_direction
            exact_match = (pd_action_direction == gt_action_direction)

        if type_match and pd_action_type == "type":
            pd_action_detail = pd_action_text
            text_dist = Levenshtein.ratio(pd_action_text, gt_action_text)
            exact_match = (pd_action_text in gt_action_text or \
                           gt_action_text in pd_action_text or \
                           text_dist > 0.8)

        if type_match and pd_action_type == "press":
            pd_action_detail = pd_action_button
            exact_match = (pd_action_button == gt_action_button)

        if type_match and pd_action_type == "stop":
            pd_action_detail = "stop"
            exact_match = True
        output_folder = os.getenv('OUTPUT_PATH',"/home/test/test03/minicpm-a/model_evaluation/aitz/CoAT-main_kun/output")
        model=os.getenv("MODEL",'minicpm')
        output_folder=os.path.join(output_folder,model,"output")
        annotate_and_save_image(gt['image_full_path'], output_folder,
                                gt_action_type, gt_action_detail,
                                pd_action_type, pd_action_detail, type_match,
                                exact_match,subset, episode_id, step_id)
        return {
            "subset": subset,
            "episode_id": episode_id,
            "step_id": step_id,
            "answer": {
                "action_type": gt_action_type,
                "action_detail": gt_action_detail
            },
            "pred": {
                "action_type": pd_action_type,
                "action_detail": pd_action_detail
            },
            "type_match": type_match,
            "exact_match": exact_match,
            "text_dist": text_dist,
            "format_hit": hit_format
        }

    def compute_episode_metrics(self, episode_results):
        success, progress = [], []
        for __, eplist in episode_results.items():
            ep_success, ep_progress = True, 0
            for ex in eplist:
                if ex['exact_match'] is True: ep_progress += 1
                else: ep_success = False
                if not ep_success: break
            success.append(ep_success)
            progress.append(ep_progress / len(eplist) * 1.0)

        return {
            "success_rate": round(sum(success) / len(success), 4),
            "goal_progress": round(sum(progress) / len(progress), 4)
        }

    def compute_atomic_metrics(self, step_results):
        recorder = {
            'total': {
                'count': 0,
                'type_match': 0,
                'exact_match': 0,
                "hit": 0
            },
            'CLICK': {
                'count': 0,
                'type_match': 0,
                'exact_match': 0
            },
            'TYPE': {
                'count': 0,
                'type_match': 0,
                'exact_match': 0,
                'text_dist': []
            },
            'SCROLL': {
                'count': 0,
                'type_match': 0,
                'exact_match': 0
            },
            'PRESS': {
                'count': 0,
                'type_match': 0,
                'exact_match': 0
            },
            'STOP': {
                'count': 0,
                'type_match': 0,
                'exact_match': 0
            },
        }

        for step in step_results:
            recorder['total']['count'] += 1
            recorder['total']['hit'] += step['format_hit']

            if step.get('answer', {}).get('action_type'):
                action_type = step['answer']['action_type'].upper()
                recorder[action_type]['count'] += 1
                recorder[action_type]['type_match'] += step['type_match']
                recorder['total']['type_match'] += step['type_match']
                recorder[action_type]['exact_match'] += step['exact_match']
                recorder['total']['exact_match'] += step['exact_match']
                if 'text_dist' in recorder[action_type] and step[
                        'text_dist'] is not None:
                    recorder[action_type]['text_dist'].append(
                        step['text_dist'])

        scores = {
            metric_key: {}
            for metric_key in
            ['total', 'CLICK', 'SCROLL', 'PRESS', 'STOP', 'TYPE']
        }
        scores['total']['hit_rate'] = round(recorder['total']['hit'] / recorder['total']['count'], 4) if \
        recorder['total']['count'] > 0 else 0
        for metric_key in [
                'total', 'CLICK', 'SCROLL', 'PRESS', 'STOP', "TYPE"
        ]:
            scores[metric_key]['type_acc'] = round(
                recorder[metric_key]['type_match'] /
                recorder[metric_key]['count'],
                4) if recorder[metric_key]['count'] > 0 else 0
            scores[metric_key]['exact_acc'] = round(
                recorder[metric_key]['exact_match'] /
                recorder[metric_key]['count'],
                4) if recorder[metric_key]['count'] > 0 else 0
        if recorder['TYPE']['text_dist']:
            scores['TYPE']['text_dist'] = round(
                sum(recorder['TYPE']['text_dist']) /
                len(recorder['TYPE']['text_dist']), 4) if len(
                    recorder['TYPE']['text_dist']) > 0 else 0
        return scores
