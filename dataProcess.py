import csv

import math

# 定义一些常量
PI = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323


def transformlat(lng, lat):
    ret = (
        -100.0
        + 2.0 * lng
        + 3.0 * lat
        + 0.2 * lat * lat
        + 0.1 * lng * lat
        + 0.2 * math.sqrt(abs(lng))
    )
    ret += (
        (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    )
    ret += (20.0 * math.sin(lat * PI) + 40.0 * math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (
        (160.0 * math.sin(lat / 12.0 * PI) + 320 * math.sin(lat * PI / 30.0))
        * 2.0
        / 3.0
    )
    return ret


def transformlng(lng, lat):
    ret = (
        300.0
        + lng
        + 2.0 * lat
        + 0.1 * lng * lng
        + 0.1 * lng * lat
        + 0.1 * math.sqrt(abs(lng))
    )
    ret += (
        (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    )
    ret += (20.0 * math.sin(lng * PI) + 40.0 * math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (
        (150.0 * math.sin(lng / 12.0 * PI) + 300.0 * math.sin(lng / 30.0 * PI))
        * 2.0
        / 3.0
    )
    return ret


def out_of_china(lng, lat):
    return (lng < 72.004 or lng > 137.8347) or (
        (lat < 0.8293 or lat > 55.8271) or False
    )


def wgs84togcj02(lng, lat):
    if out_of_china(lng, lat):
        return [lng, lat]
    else:
        dlat = transformlat(lng - 105.0, lat - 35.0)
        dlng = transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * PI
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
        mglat = lat + dlat
        mglng = lng + dlng
        return [mglng, mglat]


# 读取txt文件
with open("data.txt", "r") as txtfile:
    lines = txtfile.readlines()


# 定义将“度度分分.分分分”格式转换为度数的函数
def dms_to_deg_lontitude(dms_str):
    if len(dms_str) < 8:
        return None  # 如果长度不足，返回None
    degrees = int(dms_str[0:3])
    minutes = float(dms_str[3:])  # 将剩余部分作为分钟处理
    return degrees + minutes / 60


def dms_to_deg_latitude(dms_str):
    if len(dms_str) < 8:
        return None  # 如果长度不足，返回None
    degrees = int(dms_str[0:2])
    minutes = float(dms_str[2:])  # 将剩余部分作为分钟处理
    return degrees + minutes / 60


# 将数据转换为csv格式
csv_data = []
for i, line in enumerate(lines):
    data = line.split()
    if len(data) < 5:  # 如果缺少最后一列
        data += [""]  # 用空字符串代替
    time_str = f"{data[0][0:2]}:{data[0][2:4]}:{data[0][4:6]}"  # 格式化时间数据
    lontitude = dms_to_deg_lontitude(data[1])
    latitude = dms_to_deg_latitude(data[2])
    lontitude, latitude = wgs84togcj02(lontitude, latitude)
    csv_data.append([i, i, time_str, lontitude, latitude, data[3], data[4]])

# 写入csv文件
with open("output2.csv", "w", newline="") as csvfile:
    fieldnames = [
        "id",
        "relevant_time",
        "Time",
        "Longitude",
        "Latitude",
        "Speed",
        "Direction",
    ]
    writer = csv.writer(csvfile)
    writer.writerow(fieldnames)
    writer.writerows(csv_data)
