import scipy.integrate as integrate
from argparse import ArgumentParser
from math import cos, sin, trunc, tan, pi, sqrt
import matplotlib.pyplot as plt

def ellipsoid_pars(ell = 'wgs84'):
    # add any ellipsoid "a" and "f" here
    if ell== 'wgs84':
        # major axis
        a = 6378137.0
        f = 1/298.257223563

    elif ell=='CGCS2000':
        a = 6378137
        f = 1 / 298.257222101
    else:
        raise Exception('No such ellipsoid')
    # minor axis
    b = a * (1 - f)
    # first and second eccentricity
    e2 = 2 * f - pow(f, 2)
    e21 = (pow(a, 2) - pow(b, 2)) / pow(b, 2)
    return a, f, b, e2, e21

def geodetic_to_plane(latitude,longitude,ell='wgs84'):
    false_easting = 500000
    # convert to radiance
    # latRad = deg_to_rad(latitude)
    latRad = float(latitude)/180*pi
    # lonRad = deg_to_rad(longitude)
    # compute meridian difference and get G-K zone number
    l, n = central_meridian_diff(longitude)
    a, f, b, e2, e21 = ellipsoid_pars(ell)

    N = a / sqrt(1 - f * (2 - f) * pow(sin(latRad),2))
    t = tan(latRad)
    niu2 = e21*pow(cos(latRad),2)
    Y = lambda x :a*(1-e2)/pow(1-e2*pow(sin(x),2),3/2)
    X = integrate.quad(Y,0,latRad)[0]

    # plane coordinates

    x = X + N/2 * sin(latRad)*cos(latRad)*pow(l,2)+\
        N/24*sin(latRad)*pow(cos(latRad),3)*(5-pow(t,2)+9*niu2+4*pow(niu2,2))*pow(l,4)+N/720*sin(latRad)*pow(cos(latRad),5)*(61-58*pow(t,2)+pow(t,4))*pow(l,6)

    y = N * cos(latRad) * l + N / 6 * pow(cos(latRad) , 3) * (1 - pow(t , 2) + niu2) * pow(l , 3) + N / 120 * pow(cos(latRad) , 5 )* \
                                                                                                   (5 - 18 * pow(t , 2) + pow(t , 4) + 14 * niu2 - 58 * pow(t , 2) * niu2) * pow(l , 5)
    y += false_easting
    y = float(str(int(n)) + str(y))
    # print("x : " + str(x))
    # print("y : " + str(y))
    return x,y

def plane_to_geodetic(y,x,ell='wgs84'):
# def plane_to_geodetic(y, x, ell='CGCS2000'):
    false_easting = 500000
    a, f, b, e2, e21 = ellipsoid_pars(ell)

    m0 = a * (1 - e2)
    m2 = 3/2 * e2 * m0
    m4 = 5/4 * e2 * m2
    m6 = 7/6 * e2 * m4
    m8 = 9/8 * e2 * m6

    a0 = m0 + m2/2 + 3 * m4 /8 + 5 * m6 / 16 + 35 * m8 / 128
    a2 = m2 /2 + m4 /2 + 15 *m6/32 + 7 * m8 / 16
    a4 = m4 / 8 + 3 * m6 / 16 + 7 * m8 / 32
    a6 = m6 / 32 + m8 / 16
    a8 = m8/128

    B = []
    B.append(x/a0)
    i=0
    last = False
    while True:
        i+=1
        Bnext = (x +a2/2 * sin(2 * B[i-1]) - a4/4*sin(4*B[i-1]) + a6/6 * sin(6 * B[i-1]) - a8 / 8 * sin (8*B[i-1]))/a0
        B.append(Bnext)
        if last==True:
            Bf = B[i]
            break
        if abs(B[i] - B[i-1]) < pi/(180*60*60 * 10000):
            last = True

    n = trunc(y/ 1000000)
    y -=  (n* 1000000 + false_easting)
    L0 = n*6 - 3

    W = 1-e2*pow(sin(Bf),2)
    M = a*(1-e2)/W**(3/2)
    N = a/W**(1/2)

    t = tan(Bf)
    niu2 = e21 * pow(cos(Bf), 2)

    B = Bf - t/(2*M*N)*pow(y,2) + t/(24*M*pow(N,3))*(5 + 3*pow(t,2) + niu2 - 9*niu2*pow(t,2))*pow(y,4) - t/(720*M*pow(N,5))*(61 + 90*pow(t,2) + 45 * pow(t,4))*pow(y,6)
    l = 1/ (N * cos(Bf))*y - 1/(6 * N**3 * cos(Bf))*(1 + 2 * t**2 + niu2) * y**3 + 1/(120*N**5 * cos(Bf))*(5 + 28 * t**2 + 6 * niu2 +24 * t**4 + 8 * t**2 * niu2) * y ** 5
    lat = rad2dms(B)
    lon = rad2dms(l) + L0
    # return lat, lon
    return deg_to_rad1(lat), deg_to_rad1(lon)

def deg_to_rad(x):
    deg,min,sec = x.split(' ')
    return (float(deg) + float(min)/60 + float(sec)/3600)/180*pi

def deg_to_rad1(x):
    deg, min0 = str(x).split('.')
    min = int(min0[:2])
    sec0 = min0[2:]
    sec1 = sec0[:2]
    sec2 = sec0[2:]
    sec = sec1 + "." + sec2
    return (float(deg) + float(min)/60 + float(sec)/3600)

def central_meridian_diff(lon):
    # deg,min,sec = lon.split(' ')
    # lonDeg = float(deg) + float(min) / 60 + float(sec) / 3600
    lonDeg = float(lon)
    n = trunc(lonDeg/6)+1
    lon0 = n*6 - 3
    l = (lonDeg-lon0)/180*pi
    return l,  n

def rad2dms(radAngle):
    sign = 1
    if (radAngle < 0):
        sign = -1
        radAngle = abs(radAngle)
    secAngle = radAngle *180 /pi*3600
    degAngle = int(secAngle/3600 + 0.0001)
    minAngle = int((secAngle-degAngle*3600.0)/60.0+0.0001)
    secAngle = secAngle - degAngle*3600 - minAngle*60
    if secAngle < 0:
        secAngle = 0
    dmsAngle = degAngle+minAngle/100 + secAngle/10000
    dmsAngle = dmsAngle *sign
    return dmsAngle

print('geodetic_to_plane',geodetic_to_plane("23.16036069", "113.33990695"))
# print(geodetic_to_plane("23.160388211605742", "113.33992956650616"))
scale_world_x = []
scale_world_y = []

scale_world_x1 = []
scale_world_y1 = []
gps_flight = [["23.1604371", "113.339823"], ["23.1604372", "113.339874"],
              ["23.1604372", "113.3399251"], ["23.16048011", "113.3398215"],
              ["23.16048007", "113.3398726"], ["23.16048", "113.3399235"],

              # ["23.16044733", "113.33985680"], ["23.16041446", "113.33980694"],

              # ["23.16038532", "113.3398723"], ["23.16038529", "113.3398665"],
              # ["23.16038714", "113.3398664"], ["23.16038717", "113.3398723"],
              #
              # ["23.16034985", "113.3399022"], ["23.16034981", "113.3398993"],
              # ["23.1603553", "113.3398993"], ["23.16035537", "113.3399022"],

              # ["23.16038824476909", "113.33992669847116"], ["23.160393486984876", "113.33992659768516"], ["23.16036069", "113.33990695"],
              # ["23.160327852672985", "113.33988434211771"], ["23.1603331686706", "113.33988433416347"],
              # ["23.160327893292205", "113.33988730298508"], ["23.16033313550812", "113.33988720219742"],
              #
              # ["23.160412855498514", "113.33980449645736"], ["23.16045565494942", "113.33980603188033"], ["23.16044733", "113.3398568"],#-YAW
              # ["23.160409949224903", "113.33985546461221"], ["23.160452667940305", "113.33985688734688"],
              # ["23.160407418043803", "113.33990600739405"], ["23.160449597631672", "113.33990703564564"]]
              # ["23.160472882949712", "113.33991478394333"], ["23.16043098025981", "113.33990523408316"], ["23.16044733", "113.3398568"],#0
              # ["23.16048392868792", "113.33986513588938"], ["23.160442087404927", "113.33985571219719"],
              # ["23.160494536702675", "113.33981583628805"], ["23.160453163009265", "113.33980690236285"]]
              # ["23.160500944380864", "113.33982916503916"], ["23.16049211416704", "113.33987448266366"],["23.16044733", "113.3398568"],#90
              # ["23.160455037565264", "113.33981721913402"], ["23.160446324003548", "113.33986247032861"],
              # ["23.16040945295144", "113.33980574661832"], ["23.16040119224199", "113.3398504920984"]]
              # ["23.160411270984493", "113.33980576137736"], ["23.160454093976053", "113.3398057612879"], ["23.16044733", "113.3398568"],  # -1.9
              # ["23.160409928827555", "113.33985680572118"], ["23.160452667673326", "113.33985669590047"],
              # ["23.160408948516306", "113.33990741147672"], ["23.160451136437366", "113.33990692672144"]]
              ["23.16040972611999", "113.33980708241813"], ["23.1604525255654", "113.33980554681644"], #["23.16044733", "113.3398568"],  # -3.8
              ["23.160409949555493", "113.33985814682427"], ["23.16045266153736", "113.33985650456889"],
              ["23.160410521191988", "113.33990875990902"], ["23.160452671057758", "113.33990676267986"]]
              # ["23.160470536153525", "113.33991452073231"], ["23.160428627010525", "113.3399049701487"],
              # ["23.160481582838777", "113.3398648727855"], ["23.160439735113776", "113.33985544837105"],
              # ["23.16049219173964", "113.3398155732843"], ["23.160450811681756", "113.33980663864564"]]
              # ["23.160470536153532", "113.33991452073231"], ["23.16042862701054", "113.3399049701487"],["23.16044733", "113.3398568"],
              # ["23.160481582838788", "113.33986487278544"], ["23.160439735113787", "113.33985544837103"],
              # ["23.160492191739657", "113.33981557328427"], ["23.160450811681777", "113.33980663864564"]]

# gps_rtk = [["23.160351166666665", "113.339902"], ["23.160351166666665", "113.33989916666667"],
#        ["23.16035533333333", "113.33989916666667"], ["23.160355499999998", "113.33990216666666"]]
gps_rtk = [
           #  ["23.160351166666665", "113.339902"], ["23.160351166666665", "113.33989916666667"],
           # ["23.16035533333333", "113.33989916666667"], ["23.160355499999998", "113.33990216666666"],#1
           #
           # ["23.1603855", "113.33987233333333"], ["23.16038533333333", "113.33986633333333"],
           # ["23.160387166666666", "113.33986633333333"], ["23.1603871666", "113.339872333"],#2

           ["23.160437333", "113.33992483"], ["23.160437333", "113.339874"],
           ["23.1604371666", "113.339823"], ["23.16048", "113.3398215"],
           ["23.1604798333", "113.3398725"], ["23.16047983", "113.339923"]]
           # ["23.16044673", "113.33990786"], ["23.16051411", "113.33985755"]]

flight_rtk = [[23.16041484,	113.3399083],[23.16041483,	113.3398573],[23.16041498,	113.3398075],
              [23.16045726,	113.3398048],[23.16045751,	113.3398560],[23.16045745,	113.3399068],
              [23.16035795,	113.3399121],[23.16035761,	113.3399091],[23.16036321,	113.3399091],[23.16036312,	113.339912]]
cors_rtk = [[23.16041468,	113.3399084],[23.16041472,	113.3398575],[23.16041469,	113.3398065],
            [23.1604575,	113.339805], [23.16045731,	113.3398563],[23.16045732,	113.3399071],
            [23.16035754,	113.3399123],[23.1603574,	113.3399094],[23.16036246,	113.3399093],[23.16036261,	113.3399123]]
photo_rtk = [[23.16041460,	113.33990799],[23.16041461,	113.3398576],[23.16041454,	113.3398069],
             [23.16045701,	113.3398055],[23.16045682,	113.3398561],[23.16045684,	113.3399065],
             [23.16035782, 113.33991169],[23.16035781, 113.33990881],[23.16036314, 113.33990881],[23.16036319, 113.33991171],[23.160444972392202, 113.33985698218189]]
my_photo_rtk = [[23.16040972611999,	113.33980708241813],[23.1604525255654,	113.33980554681644],[23.160409949555493,	113.33985814682427],
             [23.16045266153736,	113.33985650456889],[23.160410521191988,	113.33990875990902],[23.160452671057758,	113.33990676267986], [23.16044733, 113.3398568]]
# my_photo_rtk = [[23.160412082342138,	113.33990625079939],[23.16041078245038,	113.3398580221638],[23.16041158789972,	113.33980951833571],
#              [23.16045223411786,	113.3398073070068],[23.160452676574444,	113.33985662207886],[23.16045238197485,	113.33990536881991], [23.16044733, 113.3398568]]
# my_photo_rtk = [[23.160424443003897,	113.33990152923647],[23.16042229112064,	113.3398576185406],[23.160424624667698,	113.33981334508202],
#              [23.160457482796105,	113.33980914259152],[23.160455507905553,	113.33985640564354],[23.160457080156327,	113.33990359452972], [23.16051411, 113.33985755]]
# my_photo_rtk = [[23.16040997203422,	113.33980602547797],[23.16045281713922,	113.33980484314696],[23.16045278582849,	113.33985611818208],
#              [23.160452681477434,	113.33990739718757],[23.16051411, 113.33985755],
#                 # [23.16035654870388, 113.33990973476402],[23.160361983359692, 113.33990954191536],[23.16036199900637, 113.33991247011392],[23.16035663506363, 113.33991258129771],[23.16036117, 113.3399066]]
#                 [23.160356366786562, 113.33990939663177], [23.16036180131187, 113.33990959373564],
#                 [23.160361637484534, 113.33991251661791], [23.160356278521267, 113.33991224309707],
#                 [23.16036117, 113.3399066]]
# my_photo_rtk = [[23.160422899271627,	113.33990612132669],[23.16041442928048,	113.33985520732818],[23.16041877411002,	113.33980433339194],
#              [23.160461573424165,	113.33980715776167],[23.160456978181053,	113.33985775106902],[23.160452760810138,	113.33990862747255], [23.16041842806645, 113.33989500238977], [23.16041884, 113.33989501]]
my_photo_rtk = [[23.16040591257295,	113.33990608792436],[23.160409582615806,	113.33985616672352],[23.160412896159322,	113.33980547001305],
             [23.160455322959855,	113.33980748601972],[23.16045177987608,	113.3398580871767],[23.160448328700294,	113.33990835605383], [23.160414427815407, 113.33985758546378], [23.16041493, 113.33985761]]

def text_precise(photo_rtk,my_photo_rtk):
    for i in photo_rtk:
        # i = geodetic_to_plane(float(i[0])+0.00002747, float(i[1])+0.00001595)
        i = geodetic_to_plane(float(i[0]), float(i[1]))
        scale_world_x.append(float(i[0]) - 2564222.1746563856)
        scale_world_y.append(float(i[1]) - 19739655.201641243)

    for i in my_photo_rtk:
        # i = geodetic_to_plane(float(i[0])+0.0000045, float(i[1]))
        i = geodetic_to_plane(float(i[0]), float(i[1]))
        scale_world_x1.append(float(i[0]) - 2564222.1746563856)
        scale_world_y1.append(float(i[1]) - 19739655.201641243)
    # 画坐标散点图
    fig = plt.figure()
    # 将画图窗口分成1行1列，选择第一块区域作子图
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.set_title('RTK')
    ax1.set_xlabel('East')
    ax1.set_ylabel('North')
    ax1.scatter(scale_world_y, scale_world_x, c='r', marker='.')
    ax1.scatter(scale_world_y1, scale_world_x1, c='b', marker='.')

    # 画直线图
    # ax1.plot(x2, y2, c='b', ls='--')
    # plt.xlim(xmax=15, xmin=-10)
    # plt.ylim(ymax=15, ymin=-10)
    # plt.legend('rice')
    plt.show()

# text_precise(photo_rtk,my_photo_rtk)
# print(scale_world_x)
# print(scale_world_y)
# print(scale_world_x1)
# print(scale_world_y1)