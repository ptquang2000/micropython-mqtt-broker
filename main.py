from server.server import Server
import network

SSID = 'Computer Network'
PASSWORD = '1921681251'
PORT = 1883

def wifi_conn():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print('Try connecting to {0}'.format(SSID))
    wlan.connect(SSID, PASSWORD)
    while wlan.isconnected() == False:
      pass
    print('Connecting to Wifi Successfully')
    return wlan

def main():
    pass

if __name__ == '__main__':
    main()