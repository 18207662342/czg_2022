from coordinate_transformation import images_processing as ip
import coordinate_transformation.coordinate_transformation as ct
import coordinate_transformation.Gauss_projection as gau

import os
from PIL import Image
import cv2
import coordinate_transformation.gps_view as gps
import matplotlib.pyplot as plt
import xlrd
def read_excel():
    latitude_longitude = []
    all_latitude_longitude = []
    book = xlrd.open_workbook('C:/czg/602/project/Uav path planning/1.code/pycharm code/photo_to_gps1.0/OUTPUT/gps_cvs/20220830-5.xlsx')
    sheet1 = book.sheets()[0]
    nrows = sheet1.nrows
    print('数据总行数：', nrows)
    ncols = sheet1.ncols
    for i in range(nrows-1):
        latitude = (sheet1.cell(i+1, 1).value)
        longitude = (sheet1.cell(i+1, 2).value)
        latitude_longitude = [latitude, longitude]
        all_latitude_longitude.append(latitude_longitude)
    return all_latitude_longitude



if __name__ == '__main__':
    ip.distortion()#去畸变，同一台无人机相机，畸变参数不用更改
    #yolov5--txt uv坐标文件
    txt_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OUTPUT\labels')
    jpg_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'INPUT\photo_text')
    cvs_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OUTPUT\gps_cvs')
    jpg_data_dir_distortion = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OUTPUT\photo_set')
    html_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OUTPUT\gps_html')
    # print(cvs_data_dir)
    os.chdir(jpg_data_dir)
    all_gps = []
    all_result = []
    for image_name in os.listdir(os.getcwd()):
        # print(image_name)
        camera_intrinsic, r, t = ct.photo_parameter(os.path.join(jpg_data_dir, image_name))
        # img_points = ct.get_rice_objection(os.path.join(jpg_data_dir_distortion, image_name), os.path.join(txt_data_dir, image_name[:len(image_name)-4])+'.txt')
        # img_points = [[60, 118], [493, 118], [63, 341], [490, 334]]
        # print('camera_intrinsic:', camera_intrinsic)
        # img_points = [[1944,438], [3109,560], [1773,1718], [2936,1837], [1613,2988],[2762,3096],[2736 - 10.14, 1824 + 0.42]]
        # img_points = [[1664, 2931], [1796, 1718], [1986, 506], [3095, 603], [2936, 1840], [2759, 3060],[2736 - 10.14, 1824 + 0.42]]
        # img_points = [[285, 2812], [282, 1700], [402, 585], [1305, 524], [1191, 1715], [1174, 2909]]
        # img_points = [[2539,1937], [2762,1937], [2759, 2048], [2539,2045]]
        # img_points = [[2349,2405], [2369,1810], [2384,1206], [2930,1205],[2912,1808], [2895,2407],[2432, 1824]]#59
        # img_points = [[3158,3129], [3165,2364], [3171,1590], [3871,1575], [3860,2344], [3848,3107], [2736 - 10.14, 1824 + 0.42]]#101-0061-0005
        img_points = [[1559,3131], [1522,1890], [1488,635], [2625,570], [2656,1826], [2688,3070], [2432, 1824]]#dji69
        img_points = [[1149,2669], [1559,1489], [1975,308], [3061,646], [2642,1833], [2229,3006],
                      [2736 - 10.14, 1824 + 0.42]]  # dji70
        # img_points = [[2303,2296], [2254,1854], [2206,1406], [2613,1345], [2656,1801], [2708,2242],
        #               [2736 - 10.14, 1824 + 0.42]]  # dji65
        img_points = [[2052,2654], [1975,1912], [1898,1162], [2576,1069], [2650,1822], [2722,2568],
                      [2736 - 10.14, 1824 + 0.42]]  # dji70
        img_points = [[291,1417], [3745,1187]]
        # print('r:', r)
        # print('t:', t)
        result = ct.pixel_to_world(camera_intrinsic, r, t, img_points)
        all_result += result
        all_gps += ct.gauss_projection(os.path.join(cvs_data_dir, image_name[:len(image_name)-4]+'.csv'), result)
    gps.draw_gps(os.path.join(html_data_dir, image_name[:len(image_name)-4]+'.HTML'), all_gps, 'red', 'orange')
    print("all_gps", all_gps)
    # os.chdir(cvs_data_dir)
    # for csv_name in os.listdir(os.getcwd()):
    #     print(csv_name)

    photo_rtk = [[23.16041460, 113.33990799], [23.16041461, 113.3398576], [23.16041454, 113.3398069],
                 [23.16045701, 113.3398055], [23.16045682, 113.3398561], [23.16045684, 113.3399065],
                 [23.16035782, 113.33991169], [23.16035781, 113.33990881], [23.16036314, 113.33990881],
                 [23.16036319, 113.33991171]]
    photo_rtk = read_excel()
    # my_photo_rtk = [[23.16040591257295, 113.33990608792436], [23.160409582615806, 113.33985616672352],
    #                 [23.160412896159322, 113.33980547001305],
    #                 [23.160455322959855, 113.33980748601972], [23.16045177987608, 113.3398580871767],
    #                 [23.160448328700294, 113.33990835605383], [23.160414427815407, 113.33985758546378],
    #                 [23.16041493, 113.33985761]]
    my_photo_rtk = all_gps
    gau.text_precise(photo_rtk, my_photo_rtk)
    # 画坐标散点图
    # scale_world_x = []
    # scale_world_y = []
    # for i in all_result:
    #     scale_world_x.append(i[0][0])
    #     scale_world_y.append(i[0][1])
    # fig = plt.figure()
    # # 将画图窗口分成1行1列，选择第一块区域作子图
    # ax1 = fig.add_subplot(1, 1, 1)
    # ax1.set_title('Result Analysis')
    # ax1.set_xlabel('scale_world_x')
    # ax1.set_ylabel('scale_world_y')
    # ax1.scatter(scale_world_x, scale_world_y, c='r', marker='.')
    # # 画直线图
    # # ax1.plot(x2, y2, c='b', ls='--')
    # # plt.xlim(xmax=8, xmin=-8)
    # # plt.ylim(ymax=6, ymin=-6)
    # plt.legend('rice')
    # plt.show()