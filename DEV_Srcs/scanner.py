import time
import concurrent.futures
import socket as sock

P_RANGE = "22~81"

addr = input("Enter Target Address : ")

start_time = time.time()

Threads = list()
splited = P_RANGE.split("~")


success_port = list()
fail_port = list()

def send_packet(port):
    session = sock.socket(sock.AF_INET,sock.SOCK_STREAM) # IPv4, TCP
    session.settimeout(.5)

    try:
        connect = session.connect_ex((addr,port))
        if connect == 0:
            success_port.append(port)
        else:
            fail_port.append(port)

    except sock.timeout:
        print("Connection Timeout")
    except OSError:
        print("Connection Error")
    finally:
        session.close()
        
    

with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    executor.map(send_packet, range(int(splited[0]),int(splited[1])))

success_port.sort()
fail_port.sort()

for i in success_port:
    print(f"Port {i} is Open")

print("==================================== line ====================================")
for i in fail_port:
    print(f"Port {i} is Closed")
    
end_time = time.time()

print(f"Time Passed : {end_time - start_time:.2f}s")