import requests

auth = "fe825afb-da21-4308-9115-8f991c5971ab"
data   = "id=1&room=Vardagsrum&temperature=19.752&ctype=NodeMCU&ip=192.168.250.111&auth=" + auth

t1="POST /api/floor/room/temp HTTP/1.1\n"
t2="Host: be9.asuscomm.com:3000\n"
t3="User-Agent: Arduino/1.0\n"
t4="Accept: */*\n"
t5="Content-Type: application/x-www-form-urlencoded\n"
t6="Content-Length: "
t61=str(len(data))
t7="\n"

datatext=t1+t2+t3+t4+t5+t6+t61+t7
print(datatext+data)

response=requests.post("http://be9.asuscomm.com:3000", datatext+data)
print(response.text)