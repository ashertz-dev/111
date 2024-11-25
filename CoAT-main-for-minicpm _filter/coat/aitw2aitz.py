import json
import os

# 安全获取嵌套字典值的函数
def safe_get(d, keys, default=None):
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key)
        else:
            return default
    return d

# 加载 JSON 文件
#file_path = '/home/test/test03/minicpm-a/model_evaluation/aitw/api_test/Qwen2-VL-7B-Instruct/web_shopping/predict.json'
file_path = os.getenv('INPUT_PATH', '/home/test/test03/minicpm-a/model_evaluation/aitw/api_test/Qwen2-VL-7B-Instruct/web_shopping/predict.json')
with open(file_path, 'r') as file:
    data = json.load(file)

# 转换 JSON 数据
#base_path = "/home/test/test03/minicpm-a/model_evaluation/aitz/CoAT-main_kun/api/qwen"
base_path=os.getenv('OUTPUT_PATH','/home/test/test03/minicpm-a/model_evaluation/aitz/CoAT-main_kun/api/')
model=os.getenv("MODEL",'minicpm')
base_path=os.path.join(base_path,model)

for item in data:
    task = item["subset"]
    episode_id = item["episode_id"]
    steps=item["steps"]
    for index,each_step in enumerate(steps):
        step_id=index
        pred=json.loads(each_step["pred"])
        # 构造 transformed_entry
        transformed_entry = {
            "action_predict": {
                "COA": {
                    "txt": {
                        "ACTION": safe_get(pred, ["action", "name"], ""),
                        "ARGS": safe_get(pred, ["action", "args"], {})
                    },
                }
            }
        }
        folder = f"{task}-{episode_id}"
        file_name = f"{folder}_{step_id}.json"
        folder_path = os.path.join(base_path, folder)
        output_path = os.path.join(folder_path, file_name)

        # 创建文件夹（如果不存在）
        os.makedirs(folder_path, exist_ok=True)

        # 保存到文件
        with open(output_path, 'w') as output_file:
            json.dump(transformed_entry, output_file, indent=4)

    print(f"Saved transformed entry to: {output_path}")
