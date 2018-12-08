import visa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import seaborn as sns; sns.set_style("whitegrid")


rm = visa.ResourceManager()
rm.list_resources()


inst = rm.open_resource('GPIB0::15::INSTR')
inst.timeout = 5000 


print(inst.query("*IDN?"))
print(rm)
print(inst)


#inst.write('SPAN?'); print(inst.read())
#inst.write('CORR?'); print(inst.read())
inst.write('POWE -40')
inst.write('LINFREQ')

inst.write('LOGM') 
#inst.write('phas') # linear scale? not sure if this is working 
inst.write('S21')


def set_range(inst, star, stop, poin):
    inst.write('STAR %d' % star)
    inst.write('STOP %d' % stop)
    inst.write('POIN %d' % poin)
    ## Can be 3, 11, 26, 51, 101, 201, 401, 801, 1601


def get_basic(inst):
    inst.write('IFBW?')
    # Can be 10, 30, 100, 300, 1000, 3000
    ifbw = float(inst.read())

    inst.write('POIN?')
    poin = float(inst.read())
    ## Can be 3, 11, 26, 51, 101, 201, 401, 801, 1601

    inst.write('star?')
    star = float(inst.read())

    inst.write('Stop?')
    stop = float(inst.read())

    inst.write('POWE?')
    powe = float(inst.read())

    return ifbw, poin, star, stop, powe
    
    
set_range(inst, 200e3, 5e9, 1601)
ifbw, poin, star, stop, powe = get_basic(inst)

print(ifbw, poin, star, stop, powe)




def get_trace(inst, m_p, s_p):
    inst.write(m_p)  
    inst.write(s_p)
    
    inst.write('FORM4;DISPDATA;OUTPFORM')
    bu = inst.read()
    bu = bu.split('\n')
    bu = [lin.split(',') for lin in bu]
    del bu[-1]
    
    
    bu = [[float(lin[0]),float(lin[1])]  for lin in bu]
    bu = pd.DataFrame(bu)

    bu['Freq'] = np.linspace(star, stop, num=int(poin))
    bu.columns = ['Real', 'Imag', 'Freq']
    
    return bu

def get_trace_b(inst, m_p, s_p):
    inst.write(m_p)  
    inst.write(s_p)
    
    data = inst.query_binary_values('FORM2;DISPDATA;OUTPFORM;', header_fmt='hp', is_big_endian=True)
    bu2 = pd.DataFrame(np.reshape(data, (int(len(data)/2),2)))    

    bu2['Freq'] = np.linspace(star, stop, num=int(poin))
    bu2.columns = ['Real', 'Imag', 'Freq']
    
    return bu2
    
    
    
   df = get_trace(inst, 'LOGM', 'S21')
   
   

df2 = get_trace_b(inst, 'LOGM', 'S21')

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(1, 1, 1)

plt.plot(df.Freq*1e-9, df.Real, label = 'ascii')#, label = df.iloc[itx].itxfiles)
plt.plot(df2.Freq*1e-9, df2.Real, label = 'binary')

plt.title('$S_{21}$', fontsize = 25)

ax.legend()
ax.set_ylabel('Magnitude (dB)', fontsize=20)
ax.set_xlabel('Frequency (GHz)', fontsize=20)


df2 = get_trace_b(inst, 'phas', 'S21')

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(1, 1, 1)

plt.plot(df.Freq*1e-9, df.Real, label = 'ascii')#, label = df.iloc[itx].itxfiles)
plt.plot(df2.Freq*1e-9, df2.Real, label = 'binary')

plt.title('S21', fontsize = 15)

ax.legend()
ax.set_ylabel('magnitude', fontsize=20)
ax.set_xlabel('Frequency (GHz)', fontsize=20)

#plt.savefig('S11' + '.png', dpi = 300, bbox_inches='tight', transparent = True)
plt.show()

plt.savefig('S11' + '.png', dpi = 300, bbox_inches='tight', transparent = True)
plt.show()
