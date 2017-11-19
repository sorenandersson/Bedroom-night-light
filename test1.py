import requests

auth = "fe825afb-da21-4308-9115-8f991c5971ab"
data   = "id=1&room=Vardagsrum&temperature=19.752&ctype=NodeMCU&ip=192.168.250.111&auth=" + auth

header="POST /api/floor/room/temp HTTP/1.1\n"
header=header+"Host: be9.asuscomm.com:3000\n"
header=header+"User-Agent: Arduino/1.0\n"
header=header+"Accept: */*\n"
header=header+"Content-Type: application/x-www-form-urlencoded\n"
header=header+"Content-Length: "
header=header+str(len(data))
header=header+"\n"

#datatext=t1+t2+t3+t4+t5+t6+t61+t7
print(header)

response=requests.post("http://be9.asuscomm.com:3000", header+data)
print(response.text)
