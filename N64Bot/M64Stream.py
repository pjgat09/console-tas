import serial
def reverse_buttons(str):
    result = ""
    for i in range(0,len(str)/4):
        result = result + str[i*4 + 3] + str[i*4 + 2] + str[i*4 + 1] + str[i*4]
    return result

def send_buttons(count):
    global button_data_sent
    if button_data_sent + count > len(all_buttons):
        count = len(all_buttons) - button_data_sent
    
    if count == 0:
        return 0
    
    end = button_data_sent + count
    
    buttons = all_buttons[button_data_sent:end]
    buttons = reverse_buttons(buttons)
    port.write(buttons)
    
    button_data_sent = button_data_sent + count
    
    return count
    
def display_buttons(frame):
    if frame * 4 + 3 >= len(all_buttons):
        return "              "
      

    start = frame*4
    end = start+4
    buttons = all_buttons[start:end]
    controls = "UDLRBAZSLRudlr"
    
    ret = ""
    if (ord(buttons[0]) & 0x08):
        ret = ret + "U"
    else:
        ret = ret + " "
    
    if (ord(buttons[0]) & 0x04):
        ret = ret + "D"
    else:
        ret = ret + " "
    
    if (ord(buttons[0]) & 0x02):
        ret = ret + "L"
    else:
        ret = ret + " "
    
    if (ord(buttons[0]) & 0x01):
        ret = ret + "R"
    else:
        ret = ret + " "
    
    if (ord(buttons[0]) & 0x40):
        ret = ret + "B"
    else:
        ret = ret + " "
        
    if (ord(buttons[0]) & 0x80):
        ret = ret + "A"
    else:
        ret = ret + " "
    
    if (ord(buttons[0]) & 0x20):
        ret = ret + "Z"
    else:
        ret = ret + " "
    
    if (ord(buttons[0]) & 0x10):
        ret = ret + "S"
    else:
        ret = ret + " "
    
    if (ord(buttons[1]) & 0x20):
        ret = ret + "L"
    else:
        ret = ret + " "
    
    if (ord(buttons[1]) & 0x10):
        ret = ret + "R"
    else:
        ret = ret + " "
    
    if (ord(buttons[1]) & 0x08):
        ret = ret + "u"
    else:
        ret = ret + " "
    
    if (ord(buttons[1]) & 0x04):
        ret = ret + "d"
    else:
        ret = ret + " "
    
    if (ord(buttons[1]) & 0x02):
        ret = ret + "l"
    else:
        ret = ret + " "
    
    if (ord(buttons[1]) & 0x01):
        ret = ret + "L"
    else:
        ret = ret + " "

    x = ord(buttons[2])
    if x > 127:
	x = (x - 128) * -1

    y = ord(buttons[3])
    if y > 127:
	y = (y - 128) * -1

    ret = ret + str(x) + " "
    ret = ret + str(y)
        
    return ret
    
port = serial.Serial("COM11", 19200, timeout=1)
port.readline();

movie = open("snark,kyman,sonicpacker,mickey_vis,tot-sm64.m64","rb")


mods_filename = "" # "filename.txt"

signature = movie.read(4)
if signature != "M64\x1A":
    print "M64 file signature not correct! This may not be an M64 movie!"

version = movie.read(4)
uid = movie.read(4)
VI_count = movie.read(4)
rerecords = movie.read(4)
rerecords = (ord(rerecords[3]) << 24) + (ord(rerecords[2]) << 16) + (ord(rerecords[1]) << 8) + ord(rerecords[0])
VIs_per_sec = movie.read(1)
print ord(VIs_per_sec)
controller_count = movie.read(1)

dummy = movie.read(2)

input_samples = movie.read(4)
movie_start = movie.read(2)

dummy = movie.read(2)

controller_flags = movie.read(4)

dummy = movie.read(160)

rom_name = movie.read(32).rstrip('\0')
rom_crc = movie.read(4)
rom_country_code = movie.read(2)

dummy = movie.read(56)

video_plugin = movie.read(64).rstrip('\0')
sound_plugin = movie.read(64).rstrip('\0')
input_plugin = movie.read(64).rstrip('\0')
rsp_plugin = movie.read(64).rstrip('\0')

author = movie.read(222).rstrip('\0')
movie_description = movie.read(256).rstrip('\0')

print "Rom:\t\t" + rom_name
print "Author:\t\t" + author
print "Description:\t" + movie_description
print "Rerecords:\t" + str(rerecords)
print "\n"

all_buttons = movie.read()
button_data_sent = 0

print len(all_buttons)
if mods_filename != "":
    mods = open(mods_filename)
    mods_lines = mods.readlines()
    mods.close
    for line in mods_lines[:]:
        mod_details = line.split(':')
        if mod_details[0] == "a":
            frame = int(mod_details[1])
            pos = frame * 4
            count = int(mod_details[2])
            print "Adding " + str(count) + " frames after " + str(frame)
            all_buttons = all_buttons[:pos] + chr(0) * (count * 4) + all_buttons[pos:]

print len(all_buttons)

send_buttons(512)

cur_frame = -1
new_frame = 0
done = 0
while 1:
    new_string = port.readline()
    if new_string != '':
        new_frame = int(new_string) / 4
        
        if new_frame != cur_frame:
            if new_frame - cur_frame > 1:
                print "SKIP...\n" * (new_frame - cur_frame - 1),
            cur_frame = new_frame
            # Clear the line
            print "\r\t\t\t\t\t\t\t\t",
            print "\rFrame: " + str(cur_frame),
            print "\t" + display_buttons(cur_frame)
            if done == 0:
                if new_frame % 128 == 1:
                    print "\tSending...",
                    if send_buttons(512) < 512:
                        done = 1
                        print "\tAll data sent!" 

