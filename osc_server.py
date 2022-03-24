from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher

def color_handler(unused_addr, x,y,c):
    """ 値を受信したときに行う処理 """
    print(f'received data : {x},{y},{c}')

IP = '127.0.0.1'
PORT = 6700

# URLにコールバック関数を割り当てる
dispatcher = Dispatcher()
dispatcher.map('/data', color_handler)

# サーバを起動する
server = osc_server.ThreadingOSCUDPServer((IP, PORT), dispatcher)
print(f'Serving on {server.server_address}')
server.serve_forever()