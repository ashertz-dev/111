import requests
import json

headers = {
    'app-code': 'gui_minicpmv_linshu',
    'app-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsInNpZ25fdHlwZSI6IlNJR04ifQ.eyJhY2Nlc3NfdG9rZW4iOiJjZ0s4QkNfajMzOUlGWjlZUlN5ZUQ0Z3JpZ0d4cjc2LXNKYmtxelFjT1o0IiwiZXhwX3RpbWUiOjI1OTIwMDAwMDAsInRpbWVzdGFtcCI6MTczMTY2MTE0ODMxMn0.klimcKw5ZtUAviAFAlB2lm9bBDHe661V1SvnL6vc0eM',
    'Content-Type': 'application/json'
}
import base64
with open("C:\\Users\\Map\\Desktop\\CoAT-main-for-minicpm\\data-example\\GOOGLE_APPS-523638528775825151\\GOOGLE_APPS-523638528775825151_1.png", "rb") as image_file:
    test=base64.b64encode(image_file.read()).decode('utf-8')
    print(test)
payload = {
    "userSafe": 0,
    "aiSafe": 0,
    "modelId": 207,
    "chatMessage": [
      {
         "role": "USER",
         "contents": [
            {
                 "type": "TEXT",
                 "pairs":  "描述这幅图片"
            },
            {
               "type": "IMAGE",
               "pairs": "https://safe-audit.oss-cn-beijing.aliyuncs.com/security/lingshu/20241113-112941.jpeg"
            },
         ]
      }
   ]
}

response = requests.post("https://gui-agent.modelbest.cn/llm/client/conv/accessLargeModel/sync", headers=headers, json=payload)

print(response.status_code)
print(response.text)
