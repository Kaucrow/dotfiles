import os
import socket

class Colors:
    HEADER = '\033[95m';
    OKBLUE = '\033[94m';
    OKCYAN = '\033[96m';
    OKGREEN = '\033[92m';
    WARNING = '\033[93m';
    FAIL = '\033[91m';
    ENDC = '\033[0m';
    BOLD = '\033[1m';
    UNDERLINE = '\033[4m';

wInterface = "";
action = "";

def InternetReachable(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout);
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port));
        return True;
    except socket.error as ex:
        return False;

def Exit(code = 0):
    print('');
    exit(code);

print('');

print("      __ __                            _    ");
print("     / //_/__ ___ _____________ _    _( )___     ");
print("    / ,< / _ `/ // / __/ __/ _ \ |/|/ //(_-<    ");
print("   /_/|_|\_,_/\_,_/\__/_/  \___/__,__/ /___/   "); 
print("     █████╗ ██████╗  ██████╗██╗  ██╗██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗     ");
print("    ██╔══██╗██╔══██╗██╔════╝██║  ██║██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║       ");
print("    ███████║██████╔╝██║     ███████║██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║     ");
print("    ██╔══██║██╔══██╗██║     ██╔══██║██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║       ");
print("    ██║  ██║██║  ██║╚██████╗██║  ██║██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗ ");
print("    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝      ");
                                                                                  
## Check if there's an internet connection available.
if (InternetReachable()):

    action = input("\nYou are not connected to the internet.\nWould you like to connect now? (y/n) ");

    if((action[0]).lower() == 'y'):

        for dir in os.listdir("/sys/class/net"):
            if dir[0] == 'w':
                wInterface = dir;
                break;

        if(wInterface == ""):
            print(Colors.FAIL + "\n[ ERR ] " + Colors.ENDC + "No wireless interface was found.");
            print("\tPlease try to connect manually and re-run the installation script.");
            Exit(1);

        os.system("iw device %s set-property Powered on" % (wInterface));
        os.system("iw station %s scan" % (wInterface));
        os.system("iw station %s get-networks" % (wInterface));

        ssid = input("Network SSID: ");
        passphrase = input("Network passphrase (leave blank for none): ");

        os.system("iw --passphrase %s station %s connect %s" % (passphrase, wInterface, ssid));

    else:
        Exit(1);

Exit(0);
