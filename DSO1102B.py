import visa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

import seaborn as sns; sns.set_style("whitegrid")



rm = visa.ResourceManager()
rm.list_resources()




inst = rm.open_resource('USB0::0x0957::0x0588::CN55222280::INSTR')
inst.timeout = 5000 

print(inst.query("*IDN?"))
print(rm)
print(inst)




#init
inst.write('*RST'); time.sleep(0.3)
inst.write(':TIMebase:MODE MAIN'); time.sleep(0.3)

inst.write(':TIMebase:MAIN:SCALe 1e-4') #Time base 1ms/div
time.sleep(0.3)
inst.write(':TIMebase:MAIN:OFFSet 0') #Time delay  = 0,
time.sleep(0.3)
inst.write(':CHANnel1:PROBe 1X') #Probe attenuation = 1x, 
time.sleep(0.3)
inst.write(':CHANnel1:SCALe 0.1') #Voltage = 2V/div
time.sleep(0.3)
inst.write(':CHANnel1:OFFSet 0.00'); time.sleep(0.3)


inst.write(':CHANnel1:COUPling DC'); time.sleep(0.3)
inst.write(':TRIGger:EDGE:SWEep NORMal'); time.sleep(0.3)
inst.write(':TRIGger:EDGE:LEVel 0.4'); time.sleep(0.3)

inst.write(':ACQuire:TYPE NORMal'); time.sleep(0.3)
inst.write(':WAVeform:POINts:MODE MAXimum'); time.sleep(0.3)


#acq
inst.write(':WAVeform:XINCrement?'); step = float(inst.read().strip()); time.sleep(0.3)
inst.write(':WAVeform:XORigin?'); orig = float(inst.read().strip()); time.sleep(0.3)
inst.write(':WAVeform:POINts?'); poin = float(inst.read().strip()); time.sleep(0.3)

inst.write(':WAVeform:FORMat RAW'); time.sleep(0.3)

inst.write(':WAVeform:DATA?'); time.sleep(1)

data = inst.read_raw()
data = data.split()
data = [line.decode('utf8').split(',')[0] for line in data]

print(data.pop(0))

data = pd.DataFrame([float(line) for line in data])
data.columns = ['Y']
data['T'] =  np.linspace(0, step*(poin+1), int(poin))


#plot
fig = plt.figure(figsize=(13, 9))
ax = fig.add_subplot(1, 1, 1)

plt.plot(data['T']*1e6, data['Y'], label = 'ascii')#, label = df.iloc[itx].itxfiles)

plt.title('$S_{21}$', fontsize = 25)

ax.legend()
ax.set_ylabel('Magnitude (V)', fontsize=20)
ax.set_xlabel('Time (usec)', fontsize=20)
plt.tick_params(axis='both', which='major', labelsize=20)


#plt.savefig('S11' + '.png', dpi = 300, bbox_inches='tight', transparent = True)
plt.show()

