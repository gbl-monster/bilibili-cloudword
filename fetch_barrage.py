import requests
import re

barrage_url = 'https://api.bilibili.com/x/v1/dm/list.so?oid=25681925910'
headers = {
    "Cookie":"buvid3=AA7396C6-088C-8C00-18AC-C88F31F4BD1017896infoc; b_nut=1725155520; _uuid=D6DDC5A8-B6BE-4B5C-3D2E-9D10A557B72E190453infoc; rpdid=|(umu)uukuk|0J'u~klulYl)); DedeUserID=27016679; DedeUserID__ckMd5=01946fdfcfa3acc3; CURRENT_QUALITY=80; hit-dyn-v2=1; buvid_fp_plain=undefined; LIVE_BUVID=AUTO5017251639765419; header_theme_version=CLOSE; enable_web_push=DISABLE; buvid4=D49483D9-0FE0-525A-E3EC-CB577E47D0E817896-024090101-zWxTcBdGFLx%2F7x9zjhdYyA%3D%3D; CURRENT_BLACKGAP=0; PVID=1; fingerprint=7283ea4de3eac46236f5131625ab5b5b; buvid_fp=7283ea4de3eac46236f5131625ab5b5b; home_feed_column=5; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzUzODY1MjYsImlhdCI6MTczNTEyNzI2NiwicGx0IjotMX0.HmoO-Xa2Hz2yrmNLIq03yEY0Xt8SzUbwPP76EHpgCpc; bili_ticket_expires=1735386466; SESSDATA=e040930b%2C1750679326%2C6c925%2Ac2CjCefckmb2bmhC7DWb5O3Ja1mdufySEkcT2SDtWL4xIc6BD6Urb9j3TOwIVYLefgL1ASVmRsajNHTUp1VGhuNklORXdFWnYwM2tweHFEY1lhUHBfQ2dLMGREVkg5YlhsdEZMX01iOThlRlgtVklGR3Z1cWtEQk1TU3ViYnROTEVNb2p3S0hNOExRIIEC; bili_jct=428f12425eb270e7e03185782ed32a8c; CURRENT_FNVAL=4048; b_lsid=269E7693_19408AD8AEE; browser_resolution=1707-791; sid=5et1pu0u; bp_t_offset_27016679=1015648092059336704",
    "Referer":"https://www.bilibili.com/video/BV1gVsSeyEAv/?spm_id_from=333.999.0.0&vd_source=9fa6f7decc60ce5c1268827ce73d8548",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
response = requests.get(url=barrage_url,headers=headers)
response.encoding = response.apparent_encoding
print(response.text)
data_list = re.findall('<d p=".*?">(.*?)</d>',response.text)
for index in data_list:
    with open('barrage.txt',mode='a',encoding='utf-8') as f:
        f.write(index)
        f.write('\n')
        print(index)
