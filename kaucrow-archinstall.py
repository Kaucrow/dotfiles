import os
import socket
import subprocess

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

class Disk:
    def __init__(self, name, size):
        self.partitions = [];
        self.name = name;
        self.size = size;

class Partition:
    def __init__(self, name, size, fs):
        self.name = name;
        self.size = size;
        self.type = "part";
        self.fs = fs;

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
    except socket.error as exc:
        return False;

def DispTitle():
    print("      __ __                            _     ");
    print("     / //_/__ ___ _____________ _    _( )___ ");
    print("    / ,< / _ `/ // / __/ __/ _ \ |/|/ //(_-< ");
    print("   /_/|_|\_,_/\_,_/\__/_/  \___/__,__/ /___/ "); 
    print("     █████╗ ██████╗  ██████╗██╗  ██╗██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗       ");
    print("    ██╔══██╗██╔══██╗██╔════╝██║  ██║██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║       ");
    print("    ███████║██████╔╝██║     ███████║██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║       ");
    print("    ██╔══██║██╔══██╗██║     ██╔══██║██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║       ");
    print("    ██║  ██║██║  ██║╚██████╗██║  ██║██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗  ");
    print("    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝\n");
    return;

def DispOptions(*options):
    for idx, option in enumerate(options, start = 1):
        print("\t(" + str(idx) + ") " + option);
      
    sel = 0;
    inputVar = input("\tSelect: ");

    if(inputVar.isdigit()):

        sel = int(inputVar);

        if(sel >= 1 and sel <= len(options)):
            return sel;

    return -1; 

def GetNthWord(num, line):
    while(num != 1):
        line = line[line.find(' ') + 1:];
        while(line[0] == ' '):
            line = line[1:];
        num -= 1;

    return line[:line.find(' ')];

def Exit(code = 0):
    print('');
    exit(code);


# Ensure the arch installation image is running in UEFI mode."
try:
    #os.listdir("/sys/firmware/efi/efivars");
    os.listdir("/");
except:
    os.system("clear");
    DispTitle();
    print(Colors.FAIL + "\n[ ERR ] " + Colors.ENDC + "The installation image is not running in UEFI mode.");
    print("\tThe installation cannot proceed.");
    Exit(1);

# Check if there's an internet connection available.
if not InternetReachable():
    wInterface = "";

    os.system("clear");
    DispTitle();

    action = input("You are not connected to the internet.\nWould you like to connect now? (y/n) ");

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

# Update the system clock.
os.system("timedatectl set-ntp true");

# Fetch the system disks and partitions.
disks = [];
process = subprocess.Popen(["lsblk", "-o", "NAME,SIZE,TYPE,FSTYPE"], stdout=subprocess.PIPE, stderr=subprocess.PIPE);
out, err = process.communicate();

lsblkOut = out.decode();
lsblkOut = lsblkOut[lsblkOut.find('\n') + 1:]; 
while(lsblkOut != ''):
    print(lsblkOut);
    data = GetNthWord(1, lsblkOut);
    
    # If the data is not a partition.
    if (len(data) == len(data.encode())):
        diskType = GetNthWord(3, lsblkOut);

        if(diskType != "disk"):
            lsblkOut = lsblkOut[lsblkOut.find('\n') + 1:];
            continue;
            
        diskName = data;
        diskSize = GetNthWord(2, lsblkOut);
        #try:
        #    diskFs = GetNthWord(4, lsblkOut[:lsblkOut.find('\n') + 1]);
        #except:
        #    diskFs = "";
        disks.append(Disk(diskName, diskSize));

    # If the data is a partition.
    else:
        partName = data[2:];
        partSize = GetNthWord(2, lsblkOut);
        partFs   = GetNthWord(4, lsblkOut[:lsblkOut.find('\n') + 1]);
        disks[len(disks) - 1].partitions.append(Partition(partName, partSize, partFs));

    lsblkOut = lsblkOut[lsblkOut.find('\n') + 1:];

selDisk = "";
while(True):
    sel = -1;
    while(sel == - 1):
        os.system("clear");
        DispTitle();
        sel = DispOptions("Partition disk", "Exit");

    match(sel):
        case 1:
            os.system("clear");
            DispTitle();

            if(selDisk == ""):
                print("\t*** DISKS ***");
                print("\tNAME\tSIZE\tTYPE\tFSTYPE");
                for disk in disks:
                    print('\t' + disk.name + '\t' + disk.size + "\tdisk");
                    for partition in disk.partitions:
                        print("\t-" + partition.name + '\t' + partition.size + "\tpart" + '\t' + partition.fs);

                diskName = input("\nInput the name of the disk to perform the installation on: ");
                for disk in disks:
                    if(diskName == disk.name and diskName[0].isalpha()):
                        selDisk = diskName;

                if(selDisk == ""):
                    print(Colors.FAIL + "[ ERR ] " + Colors.ENDC + '\"' + diskName + "\" IS NOT A VALID DISK.");

        case 2:
            Exit(0);
