import os
import shutil
from PIL import Image, ImageChops

# 计算图片相似度
def calculate_image_similarity(file_path1, file_path2):
    img1 = Image.open(file_path1).convert('RGB')
    img2 = Image.open(file_path2).convert('RGB')

    # 确保图片尺寸相同
    if img1.size != img2.size:
        return 0.0  # 如果尺寸不同，相似度为 0

    # 计算两张图片的差异
    diff = ImageChops.difference(img1, img2)

    # 计算差异值
    diff_data = list(diff.getdata())
    total_diff = sum(sum(pixel) for pixel in diff_data)  # RGB 差异的总和
    max_diff = len(diff_data) * 255 * 3  # 最大可能的差异值

    # 计算相似度
    similarity = 1 - (total_diff / max_diff)
    return similarity

# 检查文件夹中的图片是否存在高相似度图片
def has_high_similarity_images(folder_path, threshold=0.999):
    images = []
    
    # 遍历文件夹中的图片文件
    for filename in os.listdir(folder_path):
        if filename.endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp')):
            file_path = os.path.join(folder_path, filename)
            images.append(file_path)

    # 两两比较图片相似度
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            similarity = calculate_image_similarity(images[i], images[j])
            if similarity > threshold:  # 相似度超过阈值
                return True
    return False

# 递归遍历源文件夹，复制满足条件的子文件夹到目标路径，最多复制 100 个
def copy_non_duplicate_folders(src_folder, dest_folder, max_folders=100):
    copied_count = 0  # 已复制文件夹计数

    # 遍历源文件夹的子文件夹
    for root, dirs, files in os.walk(src_folder):
        for subdir in dirs:
            subdir_path = os.path.join(root, subdir)
            
            # 检查子文件夹中的图片
            if not has_high_similarity_images(subdir_path):
                # 如果没有高相似度图片，复制子文件夹到目标路径
                dest_subdir_path = os.path.join(dest_folder, os.path.relpath(subdir_path, src_folder))
                print(f"Copying folder: {subdir_path} -> {dest_subdir_path}")
                shutil.copytree(subdir_path, dest_subdir_path)
                copied_count += 1

                # 如果达到复制上限，停止复制
                if copied_count >= max_folders:
                    print(f"Reached the limit of {max_folders} folders. Stopping.")
                    return
    print(f"Total folders copied: {copied_count}")

# 设置源文件夹和目标文件夹路径

# 执行复制操作，限制最多复制 100 个文件夹
copy_non_duplicate_folders('/home/test/test03/minicpm-a/model_evaluation/aitw/dataset_test_filter/test/general', '/home/test/test03/minicpm-a/model_evaluation/aitw/filter_with_picture/test/general', max_folders=1000)
copy_non_duplicate_folders('/home/test/test03/minicpm-a/model_evaluation/aitw/dataset_test_filter/test/google_apps', '/home/test/test03/minicpm-a/model_evaluation/aitw/filter_with_picture/test/google_apps', max_folders=1000)
copy_non_duplicate_folders('/home/test/test03/minicpm-a/model_evaluation/aitw/dataset_test_filter/test/install', '/home/test/test03/minicpm-a/model_evaluation/aitw/filter_with_picture/test/install', max_folders=1000)
copy_non_duplicate_folders('/home/test/test03/minicpm-a/model_evaluation/aitw/dataset_test_filter/test/web_shopping', '/home/test/test03/minicpm-a/model_evaluation/aitw/filter_with_picture/test/web_shopping', max_folders=1000)

print("Copying completed.")


src_folder = '/home/test/test03/minicpm-a/model_evaluation/aitw/dataset_test_filter/test/general'
dest_folder = '/home/test/test03/minicpm-a/model_evaluation/aitw/filter_with_picture/test/general'