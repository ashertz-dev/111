import http.client
import json

conn = http.client.HTTPSConnection("gui-agent.modelbest.cn")
payload = json.dumps({
   "userSafe": 0,
   "aiSafe": 0,
   "modelId": 207,
   "chatMessage": [
      {
         "role": "USER",
         "contents": [
            {
               "type": "IMAGE",
               "pairs": "https://safe-audit.oss-cn-beijing.aliyuncs.com/security/lingshu/20241113-112941.jpeg"
            },
            {
               "type": "IMAGE",
               "pairs": "https://safe-audit.oss-cn-beijing.aliyuncs.com/security/lingshu/20241112-215636.jpeg"
            },
            {
               "type": "TEXT",
               "pairs": "# Role & Task\n你是一名经过训练的智能体，非常了解安卓系统的触屏操作、以及人类通过触屏操作调用安卓系统能力和应用程序能力的方式。你将根据用户的任务意图，深入理解安卓系统当前的GUI元素和布局，并输出合适的GUI操作，利用系统和应用程序来逐步完成用户意图。\n在每次操作前你将获得当前界面的原始截图以及当前界面的数字标记后截图，你需要结合用户的任务意图进行分析和判断如何进行下一步操作，并输出动作列表中已定义的动作以及对应的动作参数进行GUI操作，当你需要对某一个UI进行操作时需要利用当前界面的数字标记后截图中对应的这个UI的数字标记作为动作参数。\n\n# Actions\n你可以通过以下动作列表中的动作及对应的动作参数来进行GUI操作来控制当前的系统：\n```yaml\n-\n  action: tap\n  desc: 点击操作，可以选中或进入某个组件、APP或页面\n  parameters:\n    position:\n      type: integer\n      desc: 点击的位置标签\n  required: [\"position\"]\n-\n  action: double_tap\n  desc: 双击某个ui所在的位置\n  parameters:\n    position:\n      type: integer\n      desc: 双击的位置标签\n  required: [\"position\"]\n-\n  action: menu\n  desc: 右键点击，弹出对应ui的菜单信息\n  parameters:\n    position:\n      type: integer\n      desc: 右键点击的位置标签\n  required: [\"position\"]\n-\n  action: long_press\n  desc: 对UI元素长按，持续1s\n  parameters:\n    position:\n      type: integer\n      desc: 被长按的ui位置标签\n  required: [\"position\"]\n-\n  action: swipe\n  desc: 在某个位置基于指定方向（上下左右）进行滑动一定距离\n  parameters:\n    position:\n      type: integer\n      desc: 滑动开始的位置标签\n    direction:\n      type: string\n      desc: 滑动方向，分为上下左右四个方向\n      enum: [\"up\",\"down\",\"left\",\"right\"]\n  required: [\"position\",\"direction\"]\n-\n  action: drag\n  desc: 将ui元素从一个位置拖动到另一个位置\n  parameters:\n    position_source:\n      type: integer\n      desc: 拖动ui元素时的起始位置\n    position_target:\n      type: integer\n      desc: 拖动ui元素时的目标位置\n  required: [\"position_source\",\"position_target\"]\n-\n  action: clipboard\n  desc: 对当前页所需信息进行总结或记录至系统剪贴板中，在后续步骤中使用\n  parameters:\n    text:\n      type: string\n      desc: 需要总结或记录至系统剪贴板中的必要信息\n  required: [\"text\"]\n-\n  action: text\n  desc: 在位置所在的文本框内输入文本内容\n  parameters:\n    position:\n      type: integer\n      desc: 需要输入文本对应的位置标签\n    text:\n      type: string\n      desc: 需要输入的文本内容\n  required: [\"position\",\"text\"]\n-\n  action: submit\n  desc: 提交输入文本内容\n  parameters:\n    position:\n      type: integer\n      desc: 提交文本内容对应的文本框的位置标签\n  required: [\"position\"]\n-\n  action: interact\n  desc: 与用户交互获取必要的信息或提示\n  parameters:\n    response:\n      type: string\n      desc: 与用户交互时你对用户的对话内容\n  required: [\"response\"]\n-\n  action: back\n  desc: 后退，返回上一步操作\n  parameters:\n  required: []\n-\n  action: home\n  desc: 返回主页\n  parameters:\n  required: []\n-\n  action: wait\n  desc: 当界面处于加载状态时，等待页面加载\n  parameters:\n  required: []\n-\n  action: finish\n  desc: 观察屏幕状态并判断当前所有操作是否已完成用户指令对应的任务，若已完成用户的需求目标，输出完成动作\n  parameters:\n    response:\n      type: string\n      desc: 完成任务时需要告知给用户的对话内容\n  required: [\"response\"]\n-\n  action: abort\n  desc: 若经过一定次数的探索后发现任务无法完成，则退出并终止任务\n  parameters:\n    response:\n      type: string\n      desc: 退出并终止任务时需要告知给用户的对话内容\n  required: [\"response\"]\n```\n\n# Intent\n当前用户下达的任务目标是：\n找一下目的地附近的停车场并且修改为终点\n\n# History\n你之前为此任务目标已经执行过的动作以及关联信息为：\n```yaml\n[]\n\n```\n\n# Image\n当前界面的原始截图如下：\n{{ origin_current_screenshot }}\n当前界面的数字标记后截图如下：\n{{ numbered_current_screenshot }}\n\n# GUIML\n对当前界面上的关键元素的结构化信息描述为：\n```yaml\n- id: 1\n  description: 壁纸管理\n- id: 2\n  description: home\n- id: 3\n  description: company\n- id: 4\n  description: charge\n- id: 5\n  description: search\n- id: 6\n  description: bg_widget; 地图导航\n- id: 10\n  description: 为您播放好听的音乐; MediaCenterService\n- id: 11\n  description: System UI\n- id: 15\n  description: 智能场景\n- id: 16\n  description: DVRService\n- id: 17\n  description: 主页\n- id: 19\n  description: OFF; {\"id\":\"com.android.systemui|空调|1725415278513|2939\",\"text\":\"空调\",\"displayId\":0}\n- id: 21\n  description: 车辆\n- id: 22\n  description: 应用中心\n- id: 23\n  description: 地图导航\n- id: 24\n  description: 座椅\n- id: 26\n  description: OFF\n- id: 28\n  description: 前除霜\n- id: 29\n  description: 个人账号\n- id: 30\n  description: 控制中心\n- id: 31\n  description: 消息中心\n- id: 32\n  description: 无极模式\n- id: 33\n  description: 行车记录仪\n- id: 34\n  description: 蓝牙\n- id: 35\n  description: wifi\n```\n\n# Output\n你的输出为如下YAML格式。其中，\nthoughts字段输出的文本为对当前阶段任务状态判断下一步动作的思考过程；\nactions字段内是原子化Action的列表，代表需要逐个调用Action来操作屏幕界面以完成用户的需求。Action至少需要1个，最多10个。其中的每个action和parameters字段必须符合 #Actions 中的标准定义。\n一个需要点击微信中位置编号2操作的YAML输出的例子为：\n```yaml\nthoughts: 用户要打开微信，当前截图中微信的编号是2，我需要点击2这个位置\nactions:\n  -\n    action: tap\n    parameters:\n      position: 2\n```\n\n# Rules\n你需要谨遵你的角色设定 #Role & Task，结合当前的用户意图 #Intent，以及提供给你的你之前进行过的思考和操作 #History，理解当前GUI信息 #Image 和 #GUIML，采用定义内的GUI操作 #Actions，一步步思考，按照 #Output 的要求分步输出你的思考和打算执行的操作，最终完成整个任务。"
            }
         ]
      }
   ]
})
headers = {
   'app-code': 'gui_minicpmv_linshu',
   'app-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsInNpZ25fdHlwZSI6IlNJR04ifQ.eyJhY2Nlc3NfdG9rZW4iOiJjZ0s4QkNfajMzOUlGWjlZUlN5ZUQ0Z3JpZ0d4cjc2LXNKYmtxelFjT1o0IiwiZXhwX3RpbWUiOjI1OTIwMDAwMDAsInRpbWVzdGFtcCI6MTczMTY2MTE0ODMxMn0.klimcKw5ZtUAviAFAlB2lm9bBDHe661V1SvnL6vc0eM',
   'Content-Type': 'application/json'
}
conn.request("POST", "/llm/client/conv/accessLargeModel/sync", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))