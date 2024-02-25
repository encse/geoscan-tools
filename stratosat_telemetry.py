
#!/usr/bin/env python3
# based on https://github.com/Foxiks/StratoSat_TK-1_Decoder/blob/main/src/stratosat.py

from io import BytesIO
from os import path
from sys import argv
from datetime import datetime

def main():
    if len(argv) != 2:
        print(f'Usage: {path.basename(argv[0])} <infile>\n'
              'Process Stratosat-TK1 telemetry from hex/KISS frames.\n')
        exit(0)
    if not path.exists(argv[1]):
        print(f'File not found: {argv[1]}')
        exit(1)
    frames = parse_file(argv[1])
    data = parse_frames(frames)

def parse_file(infile):
    try:
        with open(infile, 'r') as f:
            return parse_hexfile(f)
    except UnicodeDecodeError:
        with open(infile, 'rb') as f:
            return parse_kissfile(f)


def parse_hexfile(f):
    data = []
    for row in f:
        row = row.replace(' ', '').strip()
        if '|' in row:
            row = row.split('|')[-1]
        if len(row) == 128:
            data.append(row)
    return data


def parse_kissfile(infile):
    data = []
    for row in infile.read().split(b'\xC0'):
        if len(row) == 0 or row[0] != 0:
            continue
        data.append(row[1:].replace(b'\xdb\xdc', b'\xc0').replace(b'\xdb\xdd', b'\xdb').hex(bytes_per_sep=2))
    return data


def parse_frames(data):
    offset = 0
    hr = False
    for row in data:
        if(row[:12] == '848a82869e9c'):
            telemetry_decoder(data=row)


def convert_bytes_to_int(data):
    return int.from_bytes(bytes.fromhex(data), byteorder='little')

def telemetry_decoder(data):
    data = data[32:]
    time_unix = datetime.utcfromtimestamp(convert_bytes_to_int(data[:8])).strftime('%Y-%m-%d %H:%M:%S')
    current = convert_bytes_to_int(data[8:12]) * 0.0000766
    current_pannels = convert_bytes_to_int(data[12:16]) * 0.00003076
    v_oneakb = convert_bytes_to_int(data[16:20]) * 0.00006928
    v_akball = convert_bytes_to_int(data[20:24]) * 0.00013856
    charge_all = convert_bytes_to_int(data[24:32]) * 0.00003076
    all_current = convert_bytes_to_int(data[32:40]) * 0.0000766
    t_x_p = int.from_bytes(bytes.fromhex(data[40:42]), byteorder='little', signed=True)
    t_x_n = int.from_bytes(bytes.fromhex(data[42:44]), byteorder='little', signed=True)
    t_y_p = int.from_bytes(bytes.fromhex(data[44:46]), byteorder='little', signed=True)
    t_y_n = int.from_bytes(bytes.fromhex(data[46:48]), byteorder='little', signed=True)
    t_z_p = int.from_bytes(bytes.fromhex(data[48:50]), byteorder='little', signed=True)
    t_z_n = int.from_bytes(bytes.fromhex(data[50:52]), byteorder='little', signed=True)
    t_bat1 = int.from_bytes(bytes.fromhex(data[52:54]), byteorder='little', signed=True)
    t_bat2 = int.from_bytes(bytes.fromhex(data[54:56]), byteorder='little', signed=True)
    orientation = 'Working' if int.from_bytes(bytes.fromhex(data[56:58]), byteorder='little') == 1 else 'Not working'
    cpu = int.from_bytes(bytes.fromhex(data[58:60]), byteorder='little') * 0.390625
    obc = 7476 - convert_bytes_to_int(data[60:64])
    commu = 1505 - convert_bytes_to_int(data[64:68])
    rssi = int.from_bytes(bytes.fromhex(data[68:70]), byteorder='little', signed=True) - 99
    all_packets_rx = convert_bytes_to_int(data[70:74])
    all_packets_tx = convert_bytes_to_int(data[74:78])

    print('--------------------------------------------------')
    print('Time (UTC):', time_unix)
    print('Total current:', round(float(current), 2), 'A')
    print('Current from panels:', round(float(current_pannels), 2), 'A')
    print('Voltage from one battery:', round(float(v_oneakb), 2), 'V')
    print('Total voltage:', round(float(v_akball), 2), 'V')
    print('Charging current amount:', round(float(charge_all), 2), 'A')
    print('Amount of current consumption:', round(float(all_current), 2), 'A')
    print('Temperature on X+ panel:', t_x_p, 'C')
    print('Temperature on X- panel:', t_x_n, 'C')
    print('Temperature on Y+ panel:', t_y_p, 'C')
    print('Temperature on Y- panel:', t_y_n, 'C')
    print('Temperature on Z+ panel:', t_z_p, 'C (NONE)')
    print('Temperature on Z- panel:', t_z_n, 'C')
    print('Temperature on battery 1:', t_bat1, 'C')
    print('Temperature on battery 2:', t_bat2, 'C')
    print('Orientation state:', orientation)
    print('CPU usage:', round(float(cpu), 2), '%')
    print('OBC reboots:', obc)
    print('CommU reboots:', commu)
    print('RSSI:', rssi)
    print('Number of received packets:', all_packets_rx)
    print('Number of transmitted packets:', all_packets_tx)
    print()

if __name__ == '__main__':
    main()
