import os
import random
import shutil

def copy_random_folders(src_dir, dest_dir, num_folders):
    # 确保源文件夹和目标文件夹存在
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"源文件夹 {src_dir} 不存在！")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 获取所有子文件夹
    all_folders = [os.path.join(src_dir, folder) for folder in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, folder))]
    
    # 检查子文件夹数量
    if len(all_folders) < num_folders:
        print(f"警告：源文件夹中只有 {len(all_folders)} 个子文件夹，少于需要的 {num_folders} 个。将复制所有子文件夹。")
        num_folders = len(all_folders)
    
    # 随机选择子文件夹
    selected_folders = random.sample(all_folders, num_folders)
    
    # 复制子文件夹
    for folder in selected_folders:
        folder_name = os.path.basename(folder)
        dest_folder_path = os.path.join(dest_dir, folder_name)
        shutil.copytree(folder, dest_folder_path)
        print(f"已复制文件夹：{folder} 到 {dest_folder_path}")

# 示例调用
src_directory = "/home/test/test03/minicpm-a/model_evaluation/aitw/dataset_test_filter/test/web_shopping"
dest_directory = "/home/test/test03/minicpm-a/model_evaluation/aitw/dataset_test_filter_400/test/web_shopping"
num_to_copy = 100

copy_random_folders(src_directory, dest_directory, num_to_copy)
