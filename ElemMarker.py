import ElemImage
import ElemAnalyser


# Element Marker 图像标记器

class ElemMarker:
    __image = 0
    def __init__(self, img):
        self.__image = img

    def mark_left_startpoint(self):
        pass

    def Forcemark_left_line(self, startpoint):

        flg_left_ifcp = 0   # Flag for left line inflection point

        pointset = [startpoint]
        stepring = [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]  # Step ring

        currentpoint = startpoint

        num = 0
        patnum = 0
        while True:
            num += 1
            print('<><><><><>')
            for pat in (stepring if flg_left_ifcp == 0 else stepring[2:]):
                temppoint = (currentpoint[0] + pat[0], currentpoint[1] + pat[1])
                print(pat)
                print('[当前点 : {}]'.format(temppoint))
                if self.__image.getpix(temppoint) == 1:     # 是否为白
                    patnum += 1
                    if patnum == 7:
                        patnum = 0
                    continue
                else:
                    currentpoint = temppoint
                    print('[\t加入点 : {}]'.format(currentpoint))
                    if patnum >= 3 and flg_left_ifcp == 0:
                        flg_left_ifcp = 1
                    patnum = 0
                    break
            pointset.append(currentpoint)
            if num > 100:
                break
        return pointset


    def mark_left_line(self, startpoint):
        rows = 0
        pointset = [startpoint]
        stepring = [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0)]   # Step ring


        currentpoint = startpoint
        rownum = 1
        patnum = 0
        while True:
            for pat in stepring:
                patnum += 1
                if patnum == 8:
                    patnum = 1

                temp = (currentpoint[0] + pat[0], currentpoint[1] + pat[1])
                if self.__image.getpix(temp) == 1:

                    continue
                else:
                    currentpoint = temp
                    if patnum >= 2 and patnum <= 4:
                        rownum += 1
                    break


            if pointset[-1][0] != currentpoint[0]:
                rows += 1
                pointset.append(currentpoint)
            else:
                pointset[-1] = currentpoint


            if rownum > 35:
                break
        return pointset



if __name__ == '__main__':
    path = r'C:\Users\Administrator\Desktop\ElemAnalyser_SmartCar\swap\bakup\ElemImage_cross.swp'
    # path = r'C:\Users\Administrator\Desktop\ElemAnalyser_SmartCar\swap\bakup\ElemImage_bend.swp'

    img = ElemImage.ElemImage(path)
    marker = ElemMarker(img)
    analyser = ElemAnalyser.ElemAnalyser(pixr=5, high=60, width=160, border=-1)
    analyser.loadimg(path)
    # analyser.showlines(marker.mark_left_line((59, 30)))
    analyser.showlines(marker.Forcemark_left_line((59, 30)))