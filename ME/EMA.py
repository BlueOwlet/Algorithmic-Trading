import openpyxl as xl
import tabulate
from statistics import mean

file=xl.load_workbook('Investing-Stocks.xlsx',data_only=True)
print('WorkBook Loaded')
sheets=file.worksheets
dataGenerator=sheets[1].rows
print('Data Loaded')

dataList=list(dataGenerator)
# print('Data: {}'.format(dataList[1][1].value))


counter=0
recentPrices=[]
previousma26=[]
previousma12=[]
previousma9=[]
macd=[]
signal=[]
multipliers=[2/(26+1),2/(12+1),2/(9+1)]
def EMAtest():
    global dataList
    global counter
    global macd
    global previousma12
    global previousma26
    global previousma9
    # while dataList[counter][1].value != 0:
    while counter<500:
        recentPrices.append(dataList[counter+1][1].value)
        if counter<25:
            print(recentPrices[counter])
            counter+=1
        elif counter==25:
            ma26=mean(recentPrices)
            ma12=mean(recentPrices[-12:])
            previousma26.append(ma26)
            previousma12.append(ma12)
            print('Initial Means: {}, {}'.format(ma26,ma12))
            macd.append(ma12-ma26)
            print('Initial MACD: ',macd)
            counter+=1
            print('\nCounter above 26')

        elif counter>25:
            counter+=1
            ma26=(recentPrices[-1]-previousma26[-1])*multipliers[0]+previousma26[-1]
            ma12=(recentPrices[-1]-previousma12[-1])*multipliers[1]+previousma12[-1]
            previousma26.append(ma26)
            previousma12.append(ma12)
            macd.append(ma12-ma26)
            if len(macd)==9:
                ma9=mean(macd)
                previousma9.append(mean(macd))
                signal=(macd[-1]-ma9)
                print('MACD: ',ma26,ma12,macd[-1],ma9,signal)

            elif len(macd)>9:
                ma9=(macd[-1]-previousma9[-1])*multipliers[2]+previousma9[-1]
                previousma9.append(ma9)
                macd=macd[-9:]
                signal=(macd[-1]-ma9)
                print(counter, ' | MACD1: ',ma26,ma12,macd[-1],ma9,signal)


                # print('Signal: {}'.format(signal))

    return
EMAtest()

# macd=[]
# previousma26=[]
# previousma12=[]
# previousma9=[]
# previousmacd=[]
# multipliers=[2/(26+1),2/(12+1),2/(9+1)]
# def EMA(recentPrices):
#     signal=[]
#     if len(recentPrices[0])<25:
#         pass
#     elif len(recentPrices[0])==25:
#         for i in range(len(recentPrices)):
#             ma26=mean(recentPrices[i])
#             ma12=mean(recentPrices[i][-12:])
#             macd[i].append(ma26-ma12)
#             previousma26[i].append(ma26)
#             previousma12[i].append(ma12)
#             print('initial means: {},{},{}'.format(ma26,ma12,macd[i][-1]))
#     elif len(recentPrices[0])>25:
#         for i in range(len(recentPrices)):
#             ma26=(recentPrices[i][-1]-previousma26[i][-1])*multipliers[0]+previousma26[i][-1]
#             ma12=(recentPrices[i][-1]-previousma26[i][-1])*multipliers[1]+previousma26[i][-1]
#             macd[i].append(ma26-ma12)
#             if len(macd[i])==9:
#                 ma9=mean(macd[i])
#                 previousma9[i].append(ma9)
#             elif len(macd[i])==10:
#                 ma9=(macd[i][-1]-previousma9[i][-1])*multipliers[2]+previousma9[i][-1]
#                 macd[i]=macd[i][-9:]
#                 signal.append(ma9-macd[i][-1])
#     return signal
