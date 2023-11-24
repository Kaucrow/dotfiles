import os
import socket
import subprocess
import time

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

class Tags:
    ERR = Colors.FAIL + "[ ERR ] " + Colors.ENDC;

class Disk:
    def __init__(self, name, size):
        self.name = name;
        self.size = size;
        self.parts = PartList(self);

        process = subprocess.Popen(["cat", "/sys/block/%s/size" % (self.name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE);
        byteSize, err = process.communicate();
        self.parts.startList.append(int(byteSize.decode()) * 512);

        self.freeBytes = [];
        self.freeStarts = [];
    
    def append_og(self, part):
        process = subprocess.Popen(["cat", "/sys/block/%s/%s/start" % (self.name, part.name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE);
        start, err = process.communicate();
        part.start = int(start.decode()) * 512;
        self.parts.startList.insert(len(self.parts.startList) - 1, part.start);

        process = subprocess.Popen(["cat", "/sys/block/%s/%s/size" % (self.name, part.name)], stdout=subprocess.PIPE, stderr=subprocess.PIPE);
        size, err = process.communicate();
        part.end = int(size.decode()) * 512 + part.start;
        self.parts.endList.append(part.end);
        
        self.parts.og.append(part);
        self.update_freebytes();

    def append_mod(self, part):
        part.start = self.freeStarts[self.freeBytes.index(max(self.freeBytes))];
        self.parts.startList.insert(len(self.parts.startList) - 1, part.start);

        part.end = SizeToBytes(part.size) + part.start;
        self.parts.endList.append(part.end);

        counter = 1;
        for modPart in self.parts.mod:
            if modPart.number > counter: break;
            else: counter += 1;

        part.name = self.name + str(counter);
        part.number = counter;

        self.parts.mod.insert(counter - 1, part);
        self.update_freebytes();

    def remove_part(self, part):
        replaceNum = part.number;
        for modPart in self.parts.mod:
            if modPart.number > part.number and modPart not in self.parts.og:
                modPart.number, replaceNum = replaceNum, modPart.number;
        
        self.parts.startList.remove(part.start);
        self.parts.endList.remove(part.end);
        self.parts.mod.remove(part);
        if part in self.parts.og: self.reallocParts();
        self.update_freebytes();

    def reallocParts(self):
        modPartsCopy = self.parts.mod.copy();

        for part in self.parts.mod:
            if part not in self.parts.og:
                self.remove_part(part);

        for part in modPartsCopy:
            if part not in self.parts.og:
                self.append_mod(part);

    def update_freebytes(self):
        self.freeBytes.clear();
        self.freeStarts.clear();
        self.parts.startList.sort();
        self.parts.endList.sort();

        for i in range(len(self.parts.startList)):
            space = self.parts.startList[i] - self.parts.endList[i];
            if space > 2048 * 512:
                self.freeBytes.append(space);
                self.freeStarts.append(self.parts.endList[i]);

class Part:
    def __init__(self, name, size, fs):
        self.name = name;
        if name != None: self.number = int(name[len(name) - 1]);
        else: self.number = None;
        self.size = size;
        self.start = None;
        self.end = None;
        self.use = None;
        self.fs = fs;

class PartList:
    def __init__(self, disk):
        self.og = [];
        self.mod = [];
        self.startList = [];
        self.endList = [2048];

def SizeToBytes(sizeStr):
    if not (sizeStr[len(sizeStr) - 2].isnumeric()):
        return -1;

    multiplier = sizeStr[len(sizeStr) - 1].upper();
    if not (multiplier.isalpha()):
        return -1;

    rawSize = float(sizeStr[:len(sizeStr) - 1]);
    if   multiplier == 'G': return (rawSize * 1073741824);
    elif multiplier == 'M': return (rawSize * 1048576);
    elif multiplier == 'K': return (rawSize * 1024);
    else: return -1;

def BytesToSize(byteNum):
    giga = 1073741824;
    mega = 1048576;
    kilo = 1024;

    if byteNum >= giga:
        returnVar = float("{:.1f}".format(byteNum / giga));
        return str(int(returnVar)) + 'G' if returnVar.is_integer() else str(returnVar) + 'G';
    elif byteNum >= mega:
        returnVar = float("{:.1f}".format(byteNum / mega));
        return str(int(returnVar)) + 'M' if returnVar.is_integer() else str(returnVar) + 'M';
    else:
        returnVar = float("{:.1f}".format(byteNum / kilo));
        return str(int(returnVar)) + 'K' if returnVar.is_integer() else str(returnVar) + 'K';

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

    print();

    if(inputVar.isdigit()):

        sel = int(inputVar);

        if(sel >= 1 and sel <= len(options)):
            return sel;

    return -1;

def DispSelDisk(selDisk):
    print("\t*** SELECTED DISK STATUS ***");
    print("\tNAME\tSIZE\tTYPE\tFSTYPE\tUSE");
    print('\t' + selDisk.name + '\t' + selDisk.size + "\tdisk");
    for part in selDisk.parts.mod:
        print("\t-" + part.name + '\t' + part.size + "\tpart" + '\t' + part.fs + '\t' + str(part.use));
    print();
    for space in selDisk.freeBytes:
        print("\t-FREE\t" + BytesToSize(space));
    print();

def GetNthWord(num, line):
    while(num != 1):
        line = line[line.find(' ') + 1:];
        while(line[0] == ' '):
            line = line[1:];
        num -= 1;

    return line[:line.find(' ')];

def Exit(code = 0):
    exit(code);

# ====================
# Global Variables
# ===================
action = None;
rootPartName = None;
homePartName = None;
swapPartName = None;

# Ensure the arch installation image is running in UEFI mode."
try:
    #os.listdir("/sys/firmware/efi/efivars");
    os.listdir("/");
except:
    os.system("clear");
    DispTitle();
    print('\n' + Tags.ERR + "The installation image is not running in UEFI mode.");
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
        
        else:
            print('\n' + Tags.ERR + "No wireless interface was found.");
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
    #print(lsblkOut);
    data = GetNthWord(1, lsblkOut);
    
    # If the data is not a partition.
    if (len(data) == len(data.encode())):
        diskType = GetNthWord(3, lsblkOut);

        if(diskType != "disk"):
            lsblkOut = lsblkOut[lsblkOut.find('\n') + 1:];
            continue;
            
        diskName = data;
        diskSize = GetNthWord(2, lsblkOut);
        disks.append(Disk(diskName, diskSize));

    # If the data is a partition.
    else:
        partName = data[2:];
        partSize = GetNthWord(2, lsblkOut);
        partFs   = GetNthWord(4, lsblkOut[:lsblkOut.find('\n') + 1]);
        lastDisk = disks[-1];
        lastDisk.append_og(Part(partName, partSize, partFs));

    lsblkOut = lsblkOut[lsblkOut.find('\n') + 1:];

selDisk = None;
while(True):
    sel = -1;
    while(sel == -1):
        os.system("clear");
        DispTitle();
        sel = DispOptions("Partition the disk", "Begin installation", "Exit");

    match(sel):
        case 1:
            os.system("clear");
            DispTitle();

            if(selDisk != None):
                DispSelDisk(selDisk);
                print(Colors.WARNING + '\"' + selDisk.name + "\" has already been selected as the disk to perform the installation on.");
                action = input("Would you like to reset the disk selection and partition layout? (y/n): " + Colors.ENDC);
                if action[0].lower() != 'y': continue;
                else:
                    os.system("clear");
                    DispTitle();
                    selDisk = None; 

            print("\t*** AVAILABLE DISKS ***");
            print("\tNAME\tSIZE\tTYPE\tFSTYPE");
            for disk in disks:
                print('\t' + disk.name + '\t' + disk.size + "\tdisk");
                for part in disk.parts.og:
                    print("\t-" + part.name + '\t' + part.size + "\tpart" + '\t' + part.fs);

            diskName = input("\nInput the name of the disk to perform the installation on: ");
            for disk in disks:
                if(diskName == disk.name and diskName[0].isalpha()):
                    selDisk = disk;
                    selDisk.parts.mod = disk.parts.og.copy();
                    break;

            else:
                input(Tags.ERR + '\"' + diskName + "\" is not a valid disk. ");
                continue;

            while(True):
                sel = -1;
                while(sel == -1):
                    os.system("clear");
                    DispTitle();
                    DispSelDisk(selDisk);
                    sel = DispOptions("Add a partition", "Delete a partition", "Set use", "Finish");

                match(sel):
                    # Add a partition.
                    case 1:
                        partSizeStr = input("Size (K, M, G, or blank for all available space): ").upper();
                        
                        if partSizeStr == "":
                            partSizeBytes = max(selDisk.freeBytes);
                            partSizeStr = BytesToSize(partSizeBytes);

                        else: 
                            partSizeBytes = SizeToBytes(partSizeStr);
                            if(partSizeBytes == -1):
                                input(Tags.ERR + "Invalid partition size. ");
                                continue;
                            
                            if partSizeBytes > max(selDisk.freeBytes):
                                input(Tags.ERR + "Not enough space on the selected disk. ");
                                continue;

                        knownPartFs = ["ext4", "swap", "vfat", "ntfs"];
                        partFs = input("Filesystem (ext4, swap, vfat, ntfs): ").lower();
                        if(partFs not in knownPartFs):
                            input(Tags.ERR + "Invalid partition filesystem. ");
                            continue;

                        selDisk.append_mod(Part(None, partSizeStr, partFs));

                    # Delete a partition.
                    case 2:
                        delPartName = input("Partition to delete: ");
                        delPart = None;

                        for part in selDisk.parts.mod:
                            if part.name == delPartName:
                                delPart = part;
                                break;

                        else:
                            input(Tags.ERR + "Partition \"" + delPartName + "\" was not found on the selected disk. ");
                            continue;

                        selDisk.remove_part(delPart);
                    
                    # Set partition use.
                    case 3:
                        os.system("clear");
                        DispTitle();
                        DispSelDisk(selDisk);

                        partName = input("\tPartition name: ");
                        modPart = None; 
                        
                        for part in selDisk.parts.mod:
                            
                            if part.name == partName:
                                modPart = part;
                                break;

                        else:
                            input('\n' + Tags.ERR + "Partition \"" + partName + "\" was not found on the selected disk. ");
                            continue;

                        print("\n\tPartition use")
                        sel = DispOptions("Root", "Home", "Swap");
                        if sel == -1: input(Tags.ERR + "Not a valid option. "); continue;

                        class Exc:
                            useAlreadyAssigned = Tags.ERR + "This use has already been assigned to a partition. ";
                            fsNotCompat = Tags.ERR + "This use cannot be given to a partition of type \"%s\". ";
                        try:
                            match(sel):
                                case 1:
                                    if modPart.fs != "ext4": raise Exception(Exc.fsNotCompat % (modPart.fs));
                                    elif rootPartName != None: raise Exception(Exc.useAlreadyAssigned);
                                    modPart.use = "root";
                                    rootPartName = modPart.name;
                                case 2:
                                    if modPart.fs != "ext4": raise Exception(Exc.fsNotCompat % (modPart.fs));
                                    elif homePartName != None: raise Exception(Exc.useAlreadyAssigned);
                                    modPart.use = "home";
                                    homePartName = modPart.name;
                                case 3:
                                    if modPart.fs != "swap": raise Exception(Exc.fsNotCompat % (modPart.fs));
                                    elif swapPartName != None: raise Exception(Exc.useAlreadyAssigned);
                                    modPart.use = "swap";
                                    swapPartName = modPart.name;
                        except Exception as exc:
                            input(exc);

                    # Finish partitioning.
                    case 4:
                        break;

    # Perform installation.
        case 2:
            if rootPartName == None: 
                print(Tags.ERR + "No root partition was specified. The installation cannot proceed.\n");
                Exit(1);

            for part in selDisk.parts.og:
                if part not in selDisk.parts.mod:
                    os.system("echo \"wipefs -a /dev/%s\"" % (part.name));
                    os.system("echo \"d\n%s\nw\" | fdisk /dev/%s" % (part.number, selDisk.name));
                    time.sleep(1);

            for part in selDisk.parts.mod:
                if part not in selDisk.parts.og:
                    os.system("echo \"n\n%s\n\n+%s\nw\" | fdisk /dev/%s" % (part.number, part.size, selDisk.name));
                    time.sleep(1);

            Exit(0);

        # Exit program.
        case 3:
            Exit(0);