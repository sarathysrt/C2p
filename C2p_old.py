import bwr as bwr
import pandas as pd
from scipy.signal import butter, lfilter
import numpy as np
import sys, os
def bandpass_filter( data, lowcut, highcut, signal_freq, filter_order):
    #nyquist_freq = 0.5 * signal_freq
    #print('****')
    #print(nyquist_freq)
    #low = lowcut / nyquist_freq
    #print(low)
    #high = highcut / nyquist_freq
    #print(high)
    #b, a = butter(filter_order, [low, high], btype="band")
    #print(b,a)
    #y = lfilter(b, a, data) 
    
    y=data
    return y
def Find_peak(data1,rolling=40,spacing=1.5):
    data=pd.DataFrame(data1)
    data.columns=['Record']
    mx=np.max(data.Record)/4
    #ak=(np.max(data.Record)+np.min(data.Record))/2
    dataqw = [mx for i in data.Record]
    window = []
    peaklist = []
    listpos = 0 #We use a counter to move over the different data columns
    for datapoint in data.Record:
        rollingmean = dataqw[listpos] #Get local mean
        if (datapoint < rollingmean) and (len(window) < 1): #If no detectable R-complex activity -> do nothing
            listpos += 1
        elif (datapoint >= rollingmean): #If signal comes above local mean, mark ROI
            window.append(datapoint)
            listpos += 1
        else: #If signal drops below local mean -> determine highest point
            if len(str(rollingmean))==0:
                print(1)
            else:
                maximum = max(window)
                beatposition = listpos - len(window) + (window.index(maximum)) #Notate the position of the point on the X-axis
                peaklist.append(beatposition) #Add detected peak to list
                window = [] #Clear marked ROI
                listpos += 1
    return np.sort(peaklist)

def Q_peak(data,q_index):      
    i_point=0   
    q_list=[]
    for Qpoint in q_index:
        Int_measure_points = data[i_point:Qpoint]
            #Int_measure_points = Int_meas[0:195]
        Len_size=len(Int_measure_points)
        pos=0
        gate_enable=0
        for s in range(Len_size):
            t1=Int_measure_points[Len_size-(1+s)]
            t2=Int_measure_points[Len_size-(2+s)]
            if(t1>=t2):                    
                pos+=1
            else:
                if(gate_enable==0):
                    q_list.append((Len_size-(s+1)+i_point))
                    gate_enable=2
        i_point=Qpoint
    return np.sort(q_list)
def P_peak(data,Q_list):
    p_frequency= round(len(data)*0.02)
    P_list=[]
    #P_list_trail=[x-p_frequency for x in Q_list]
    P_list_trail=[]
    for i in Q_list:
        tmp=i-p_frequency
        if(tmp<=0):
            P_list_trail.append(0)
        else:
            P_list_trail.append(tmp)
    for sp in range(len(P_list_trail)):
        sk=data[P_list_trail[sp-1]:Q_list[sp-1]]
        Max_p_val=np.max(sk)
        P_max_index = np.where(sk==Max_p_val)
        P_list.append(np.min(P_list_trail[sp-1])+np.min(P_max_index[0]))

    return np.sort(P_list)

def min_max_correction(data,List1,List2,tp):
    Corr_data=[] 
    len_list=len(List1)
    for dp in range(len_list):
        sk=data[List1[dp]:List2[dp]]
        if(tp=='max'):
            Max_p_val=np.max(sk)
        else:
            Max_p_val=np.min(sk)
            
        P_max_index = np.where(sk==Max_p_val)
        Corr_data.append(np.min(List1[dp])+np.min(P_max_index[0])) 
        
    return np.sort(Corr_data)

def Peak_correction(data,pt):
    Peak_correction=[]
    for Dpoint in data:
        if(Dpoint>=0 and pt=='S'):
            Peak_correction.append(0)
        elif(Dpoint<=0 and pt=='R'):
            Peak_correction.append(0)
        else:
            Peak_correction.append(Dpoint)
    Peak_correction=np.asarray(Peak_correction)
    Peak_correction=Peak_correction**2
    return Peak_correction

def Data_Correction(data,image_type,baseline):
    if(image_type=='inverted'):
        max_hr=(np.max(data))
        ecg_measurements = [max_hr-x for x in data]
    else:
        ecg_measurements = data
    (baseline, ecg_measurements1) = bwr.bwr(ecg_measurements)
    x1=np.min(ecg_measurements1)*-1
    Data = [x1+x for x in ecg_measurements1]
    return Data
def T_peak(data,P_list,Q_list,R_list,S_list,Buffer_frequency,data_len):
    t_corr_p_list=P_list-round(Buffer_frequency)
    k=0
    
    for i in t_corr_p_list:
        if(i<0):
            t_corr_p_list[k]=0
            k+=1
        else:
            k+=1
    
    #print(t_corr_p_list,P_list,Q_list,R_list,S_list)
    ds=[]
    k=0
    for i in range(data_len):
        if(i>S_list[k]):
            if(k<len(S_list)-1):
                k+=1
    #print(k,len(S_list))
        if(i>=t_corr_p_list[k] and i<=S_list[k]):
            ds.append(0)
        #ds.append(data[i]%2)
        else:
            ds.append(float(data[i])**2)
            #print(float(data[i]))
    

    if(P_list[0]<Q_list[0] and P_list[0]<R_list[0] and P_list[0]<S_list[0]):
        pk=[0 for x in range(P_list[0])]
        ds[:P_list[0]]=pk
    ps=[0 for x in range(len(ds[S_list[-1]:]))]
    ds[S_list[-1]:data_len]=ps
    #print(ds)
    s=0
    open_flag=0
    first_flag=0
    o_array=[]
    c_array=[]

    for k in ds:
        if(k==0):
            if(open_flag==1 and first_flag==1):
                c_array.append(s-1)
                first_flag=0
            elif(open_flag==1):
                ops=1
            else:
                open_flag=1
            s+=1
        else:
            if(open_flag==1 and first_flag==0):
                o_array.append(s)
                first_flag=1
            s+=1
    print('A*')
    #print(ds)
    T_list = min_max_correction(ds,o_array,c_array,'max')
    return T_list

def Get_PQRS(data1):
    ecg_measurements=Data_Correction(data1,image_type='inverted',baseline='Yes')
    
    # step 1: Measurements filtering - 0-15 Hz band pass filter.
    signal_frequency = 100
    filtered_ecg_measurements = bandpass_filter(ecg_measurements, lowcut=0.0,highcut=15.0, signal_freq=signal_frequency,filter_order=1)
    # add this back when you add bandpass
    #filtered_ecg_measurements[:5] = filtered_ecg_measurements[5]

    #step 2: Derivative - provides QRS slope information.
    differentiated_ecg_measurements = np.ediff1d(filtered_ecg_measurements)
    
    data=ecg_measurements
    data_len=len(data)
    pps=round(data_len/10)
    
    Buffer_frequency=round(data_len*0.02)
    S_list = Find_peak(Peak_correction(differentiated_ecg_measurements,pt='S'))
    R_list = Find_peak(Peak_correction(differentiated_ecg_measurements,pt='R'))
    Q_list = Q_peak(data,R_list)
    trial_S_list= S_list+Buffer_frequency#round(data_len*0.002)
    trial_P_list= Q_list-Buffer_frequency
    P_list = P_peak(data,Q_list)
    
    #P_list = min_max_correction(ecg_measurements,Q_list,trial_P_list,'max')
    R_list = min_max_correction(data,P_list,S_list,'max')
    Q_list = min_max_correction(data,P_list,R_list,'min')
    S_list = min_max_correction(data,S_list,trial_S_list,'min')
    T_list=T_peak(data,P_list,Q_list,R_list,S_list,Buffer_frequency,data_len)
    
    RR_Mean= round(np.mean([R_list[i+1]-R_list[i] for i in range(len(R_list)-1)]))
    QRS_Mean= round(np.mean([S_list[i]-Q_list[i] for i in range(len(Q_list))]))
    PQ_Mean= round(np.mean([Q_list[i]-P_list[i] for i in range(len(Q_list))]))
    QT_Mean= round(np.mean([T_list[i]-Q_list[i] for i in range(len(T_list))]))
    ST_Mean= round(np.mean([T_list[i]-S_list[i] for i in range(len(T_list))]))
    
    PP_std= round(np.std([P_list[i+1]-P_list[i] for i in range(len(P_list)-1)]))
    RR_std= round(np.std([R_list[i+1]-R_list[i] for i in range(len(R_list)-1)]))
    QQ_std= round(np.std([Q_list[i+1]-Q_list[i] for i in range(len(Q_list)-1)]))
    SS_std= round(np.std([S_list[i+1]-S_list[i] for i in range(len(S_list)-1)]))
    TT_std= round(np.std([T_list[i+1]-T_list[i] for i in range(len(T_list)-1)]))
    
    Qrs_seg=str(round((QRS_Mean/pps),2))
    PQ_seg=str(round((PQ_Mean/pps),2))
    QT_seg=str(round((QT_Mean/pps),2))
    ST_seg=str(round((ST_Mean/pps),2))
    bpm=round(60/(RR_Mean/(round(data_len*0.1))))
    
    aDict = {}
    aDict['Heart rate (BPM)'] = bpm
    aDict['QRS Segment length(Sec)'] = Qrs_seg
    aDict['PQ Segment length(Sec)'] = PQ_seg
    aDict['QT Segment length(Sec)'] = QT_seg
    aDict['ST Segment length(Sec)'] = ST_seg
    aDict['PQRST standard Dev'] = PP_std,QQ_std,RR_std,SS_std,TT_std
    return aDict

def main_Call(data):
    try:
        aDict=Get_PQRS(data)
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        aDict = {}
        aDict['Heart rate (BPM)'] = '0.00'
        aDict['QRS Segment length(Sec)'] = '0.00'
        aDict['PQ Segment length(Sec)'] = '0.00'
        aDict['QT Segment length(Sec)'] = '0.00'
        aDict['ST Segment length(Sec)'] = '0.00'
        aDict['PQRST standard Dev'] = ['0.00', '0.00', '0.00', '0.00', '0.00']
        aDict['ErrorMessage'] = str(e)
        aDict['ErrorLine'] = str(exc_tb.tb_lineno)
        #aDict['ErrorType'] = str(exc_type)
    return aDict
