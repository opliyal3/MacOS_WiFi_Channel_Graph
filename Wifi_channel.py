import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

pd.options.mode.chained_assignment = None  # default='warn'


def find_channel(password):
    set_airport = f"echo '{password}' | sudo -S -k ln -s /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport /usr/local/bin/airport"

    try:
        subprocess.Popen(set_airport, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except:
        exit()
    scan = subprocess.Popen('airport -s', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    scan_out, scan_err = scan.communicate()
    scan_out_lines = str(scan_out).split("\\n")
    scan_out_lines = str(scan_out).split("\\n")[1:-1]

    new_list = list()
    max_len = 0
    for i in scan_out_lines:
        i = i.lstrip().rstrip()
        split_line = [e for e in i.split(" ") if e != ""]
        max_len = max(len(split_line), max_len)

        if len(split_line[1]) != 17 and ':' not in split_line[1]:
            split_line[0] += split_line[1]
            split_line.pop(1)
            new_list.append([split_line[0], split_line[2], split_line[3]])
        else:
            new_list.append([split_line[0], split_line[2], split_line[3]])

    df = pd.DataFrame(new_list, columns=['SSID', 'RSSI', 'Channel'])
    NaN = np.nan
    df['r_range'] = NaN
    df['l_range'] = NaN
    df['Bandwidth'] = ''

    # find channel range
    for row, column in enumerate(df.values):
        if '+1' in column[2]:
            df['r_range'][row] = float(column[2][0:-3]) + 2 - 4
            df['l_range'][row] = float(column[2][0:-3]) + 2 + 4
            df['Channel'][row] = str(int(column[2][0:-3]))
            df['Bandwidth'][row] = '40MHz'

        elif '-1' in column[2]:
            df['r_range'][row] = float(column[2][0:-3]) - 2 - 4
            df['l_range'][row] = float(column[2][0:-3]) - 2 + 4
            df['Channel'][row] = str(int(column[2][0:-3]))
            df['Bandwidth'][row] = '40MHz'

        else:
            df['r_range'][row] = float(column[2]) - 2
            df['l_range'][row] = float(column[2]) + 2
            df['Bandwidth'][row] = '20MHz'

        # if channel > 11, not 2.4Ghz, delete from df
        try:
            if int(column[2]) > 11:
                df.drop([row], inplace=True)
        except:
            continue

    # change type, sorted by channel
    df['RSSI'] = df['RSSI'].astype(str).astype(int)
    df['Channel'] = df['Channel'].astype(str).astype(int)
    df = df.sort_values(by='Channel')
    # reset index
    df = df.reset_index(drop=True)

    return df


def get_color():
    df_color = find_channel(password)
    all_color = list()

    for c in range(0, len(df_color.index)):
        rgb = np.random.rand(3, )
        all_color.append(rgb)
    return all_color


def draw_graph():
    wifi = find_channel(password)

    plt.cla()

    plt.xlabel('Wifi Channel')
    plt.ylabel('Signal Strength [dBm]')

    plt.grid(axis='y', linestyle='--')
    plt.grid(axis='x', linestyle=':', color='r', alpha=0.3)

    y_major_ticks = np.arange(0, -100, -10)
    plt.gca().set_yticks(y_major_ticks)

    x_major_ticks = np.arange(0, 15, 1)
    plt.gca().set_xticks(x_major_ticks)

    plt.ylim(-100, 0)
    plt.xlim(-2, 16)

    for index, row in wifi.iterrows():
        diff = (row['l_range'] - row['r_range'])
        x = np.linspace(row['r_range'], row['l_range'], 50)
        y = (-99 - row['RSSI']) * np.sin((x - row['r_range']) / diff * np.pi)
        y = -99 - y

        color = get_color()[index % len(get_color())]

        plt.fill(x, y, color=color, alpha=0.3)
        plt.plot(x, y, color=color)
        plt.text(row['Channel'], row['RSSI'] + 1, row['SSID'], horizontalalignment='center')
    plt.show()


if __name__ == '__main__':
    password = sys.argv[0]
    # password = 'affinity'
    # print(wifi_mac(password))
    print(find_channel(password))
    get_color()
    draw_graph()
