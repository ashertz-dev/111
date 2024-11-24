from PIL import Image, ImageDraw
import json
json_data = '''
    {
        "subset": "general",
        "episode_id": "7793064798849055148",
        "step_id": 4,
        "answer": {
            "action_type": "click",
            "action_detail": [
                90,
                263
            ]
        },
        "pred": {
            "action_type": "click",
            "action_detail": [
                134,
                -70,
                269,
                200
            ]
        },
        "type_match": true,
        "exact_match": false,
        "text_dist": null,
        "format_hit": true
    }
'''

# 解析JSON字符串
data = json.loads(json_data)
base_path="C:\\Users\\Map\\Desktop\\android_in_the_zoo\\test"
check_path=base_path+"/"+data["subset"]+"/"+data["subset"]+"-"+data["episode_id"]+"/"+data["subset"]+"-"+data["episode_id"]+"_"+str(data["step_id"])+".png"
print(check_path)
print(data)
# 使用示例
# 打开图片
image = Image.open(check_path)

# 创建一个可用于绘图的对象
draw = ImageDraw.Draw(image)

# 绘制实际点击点
red_color = (255, 0, 0)
x=data["answer"]["action_detail"][0]
y=data["answer"]["action_detail"][1]
# 在指定位置绘制一个红点（通过绘制一个小圆实现）
draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=red_color)

#绘制预测点击点
yellow = (255, 255, 0)
x=(data["pred"]["action_detail"][0]+data["pred"]["action_detail"][2])/2
y=(data["pred"]["action_detail"][1]+data["pred"]["action_detail"][3])/2
# 在指定位置绘制一个红点（通过绘制一个小圆实现）
draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=yellow)
left_top=(data["pred"]["action_detail"][0],data["pred"]["action_detail"][1])
right_bottom=(data["pred"]["action_detail"][2],data["pred"]["action_detail"][3])
draw.rectangle([left_top, right_bottom], outline='yellow')
# 保存修改后的图片
image.save("10.png")
