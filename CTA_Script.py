import xml.etree.ElementTree as ET
import requests
import time
from collections.abc import MutableMapping
from contextlib import suppress
import board
import busio
import digitalio
import adafruit_tlc5947

spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
DRIVER_COUNT = 8  # change this to the number of drivers you have chained
LATCH = digitalio.DigitalInOut(board.D5)
tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH, num_drivers=DRIVER_COUNT, auto_write = False)


class rundata:
    def __init__(self):
        #defines a dictionary with sub-dictionaries for each of the 8 train lines - does not reinitialize each run
        self.run_stations={'blue':{},'brn':{},'g':{},'org':{},'pink':{},'p':{},'red':{},'y':{}}
        #stores the api key in the class self variables
        self.api_key = 'Enter Your CTA API key here'
        #list of currently active runs - reinitializes every call
        self.runlist=[]
        #list of trains that have left service since last call
        self.keylist=[]
        #list of line Id's with full names
        self.true_station = {'blue':'Blue',
                             'brn':'Brown',
                             'g':'Green',
                             'org':'Orange',
                             'pink':'Pink',
                             'p':'Purple',
                             'red':'Red',
                             'y':'Yellow',
                             }
        self.results=[]
        #list of station ID's to light concatenated with line ID
      
    def stationpoll(self):
        
        #defines the parameters for the api call
        parameters ={"key":self.api_key,"rt":self.run_stations}

        while True:
            try:
                response = requests.get('http://lapi.transitchicago.com/api/1.0/ttpositions.aspx?',params=parameters)
                break
            except:
                tlc5947[59] = 800
                tlc5947.write()
                pass
            
        traindata = ET.fromstring(response.content)#Read XML into traindata element
        #print(traindata.text,'\n','\n','**********','\n')
        return traindata
    
    def data_parsing(self,traindata):
        self.runlist = []
        for route in traindata.findall('route'):  #Iterates each route of the XML
            linename = route.get('name')    #Assigns the defined route name to variable 'linename'
            for train in route.findall('train'):    #Iterates each train with a route of the XML
                runID = int(train.find('rn').text)  #Assigns the run ID number to the variable 'runID'
                atstation = int(train.find('isApp').text)    #Assigns the station arrival status (0 or 1) to the variable 'atstation'
                stationID = int(train.find('nextStaId').text)   #Assigns the station ID number to the variable 'stationID'
                stationName = train.find('nextStaNm').text    #Assigns the station name to the variable 'stationName'
                self.runlist.append(runID)
                
                if atstation ==  1: #for trains that are indicating arrival at a station within 1 minute 
                        self.run_stations[linename][runID]= {stationID}    #add the train runID and station ID to the run_stations dict

    def find_trains_out_of_service(self):
        self.keylist= []    #initialize keylist variable
        
        for p_id,p_info in self.run_stations.items(): #loop over each parent key and then child key
            for key in p_info: #loop over each item key
                if not key in self.runlist: #compare key of run_stations to that of runlist
                    self.keylist.append(key) #add trains that are no longer in runlist but exist in run_stations to the keystation list

       #return self.run_stations
    
    def delete_keys_from_dict(self,dictionary,keys): #This function is some elegant wizardry from the internet
        for key in keys:
            with suppress(KeyError):
                del dictionary[key]
        for value in dictionary.values():
            if isinstance(value, MutableMapping):
                self.delete_keys_from_dict(value,keys)
                
    def master(self):
        self.results=[]
        traindata = self.stationpoll() #pull api data
        self.data_parsing(traindata) # parse the data
        self.find_trains_out_of_service() #determine trains out of service since last call
        self.delete_keys_from_dict(self.run_stations,self.keylist) #delete trains in run_stations that are out of service
        #print("\n Run numbers that have left service since last call \n",self.keylist)
        #print("\n Runs in service \n", self.runlist)
        #print("\n Runs and corresponding Station ID's that should be lit", "\n Either previous station (while enroute) or current station \n")
        for key in self.run_stations:
            #print('*******', self.true_station[key],'*********','\n')
            for ID in self.run_stations[key]:
                #print(self.run_stations[key][ID],'\n')
                stationnum = (self.run_stations[key][ID])
                self.results.append(key + str(stationnum))
        #print(self.results)
        return self.results


   
def iomapping(stationID):
    ChannelLookup= {
            "brn{40730}":0,
            "p{40730}":1,
            "org{40730}":2,
            "pink{40730}":3,
            "pink{40380}":4,
            "blue{40380}":5,
            "blue{40370}":6,
            "blue{40790}":7,
            "pink{40040}":8,
            "org{40040}":9,
            "p{40040}":10,
            "brn{40040}":11,
            "blue{40070}":12,
            "pink{40160}":13,
            "org{40160}":14,
            "p{40160}":15,
            "brn{40160}":16,
            "blue{41340}":17,
            "brn{40460}":18,
            "p{40460}":19,
            "brn{40380}":20,
            "p{40380}":21,
            "org{40380}":22,
            "g{40380}":23,
            "pink{40680}":24,
            "g{40680}":25,
            "org{40680}":26,
            "p{40680}":27,
            "brn{40680}":28,
            "pink{41700}":29,
            "g{41700}":30,
            "org{41700}":31,
            "p{41700}":32,
            "brn{41700}":33,
            "y{41680}":34,
            "y{40140}":35,
            "brn{40850}":36,
            "p{40850}":37,
            "org{40850}":38,
            "pink{40850}":39,
            "red{40560}":40,
            "red{41090}":41,
            "red{41660}":42,
            "pink{40260}":43,
            "g{40260}":44,
            "org{40260}":45,
            "p{40260}":46,
            "brn{40260}":47,
            "p{40520}":48,
            "p{40400}":49,
            "p{41250}":50,
            "p{41050}":51,
            "BLANK{CHANNEL}":52,
            "p{40540}":53,
            "red{40540}":54,
            "red{40770}":55,
            "red{41200}":56,
            "red{40340}":57,
            "red{41380}":58,
            "STATION{CHANNEL}":59,
            "red{40880}":60,
            "red{40760}":61,
            "red{41300}":62,
            "red{40100}":63,
            "red{41190}":64,
            "red{40900}":65,
            "p{40900}":66,
            "y{40900}":67,
            "p{40840}":68,
            "p{40270}":69,
            "p{40690}":70,
            "p{40050}":71,
            "p{41320}":72,
            "brn{41320}":73,
            "brn{40360}":74,
            "brn{41310}":75,
            "red{41420}":76,
            "red{40080}":77,
            "red{40330}":78,
            "p{40710}":79,
            "brn{40710}":80,
            "red{41450}":81,
            "red{40630}":82,
            "red{40650}":83,
            "brn{40800}":84,
            "p{40800}":85,
            "brn{40660}":86,
            "p{40660}":87,
            "brn{41220}":88,
            "p{41220}":89,
            "red{41220}":90,
            "brn{40530}":91,
            "p{40530}":92,
            "brn{41210}":93,
            "p{41210}":94,
            "red{41320}":95,
            "g{41120}":96,
            "g{40300}":97,
            "red{40190}":98,
            "g{41270}":99,
            "red{41230}":100,
            "g{41080}":101,
            "g{40130}":102,
            "red{41170}":103,
            "g{40510}":104,
            "g{40720}":105,
            "g{41140}":106,
            "red{40910}":107,
            "g{40940}":108,
            "red{40990}":109,
            "red{40240}":110,
            "red{41430}":111,
            "red{40450}":112,
            "g{40290}":113,
            "red{41000}":114,
            "g{41690}":115,
            "org{41400}":116,
            "g{41400}":117,
            "red{41400}":118,
            "red{41490}":119,
            "org{40930}":120,
            "org{40960}":121,
            "org{41150}":122,
            "org{40310}":123,
            "blue{40390}":124,
            "blue{40980}":125,
            "blue{40180}":126,
            "blue{40010}":127,
            "blue{40970}":128,
            "blue{40920}":129,
            "pink{41030}":130,
            "pink{40830}":131,
            "pink{40580}":132,
            "pink{40420}":133,
            "pink{40600}":134,
            "pink{40150}":135,
            "pink{40780}":136,
            "pink{41040}":137,
            "pink{40440}":138,
            "pink{40740}":139,
            "org{41130}":140,
            "pink{40210}":141,
            "org{41060}":142,
            "org{40120}":143,
            "blue{40250}":144,
            "g{41360}":145,
            "g{41070}":146,
            "g{41670}":147,
            "g{40030}":148,
            "g{40480}":149,
            "g{40700}":150,
            "g{40280}":151,
            "g{41260}":152,
            "g{40610}":153,
            "g{41350}":154,
            "g{40020}":155,
            "blue{40490}":156,
            "g{41160}":157,
            "pink{41160}":158,
            "g{41510}":159,
            "pink{41510}":160,
            "g{40170}":161,
            "pink{40170}":162,
            "blue{40430}":163,
            "blue{40350}":164,
            "blue{40470}":165,
            "blue{40810}":166,
            "blue{40220}":167,
            "blue{40670}":168,
            "blue{40570}":169,
            "blue{41020}":170,
            "blue{40060}":171,
            "blue{41240}":172,
            "blue{40550}":173,
            "blue{41330}":174,
            "blue{41280}":175,
            "blue{40750}":176,
            "blue{40230}":177,
            "blue{40820}":178,
            "blue{40890}":179,
            "brn{41440}":180,
            "brn{41460}":181,
            "brn{41500}":182,
            "brn{40090}":183,
            "brn{41480}":184,
            "brn{41010}":185,
            "brn{40870}":186,
            "brn{41180}":187,
            "brn{41290}":188,
            "blue{41410}":189,
            "blue{40320}":190,
            "blue{40590}":191,
            }
    
    channel= ChannelLookup[stationID]
    return channel

def pwmlookup(channel):
    PWMLookup= {
       0:300,
1:350,
2:3000,
3:700,
4:700,
5:550,
6:550,
7:550,
8:700,
9:3000,
10:350,
11:300,
12:550,
13:700,
14:3000,
15:350,
16:300,
17:550,
18:300,
19:350,
20:300,
21:350,
22:3000,
23:175,
24:700,
25:175,
26:3000,
27:350,
28:300,
29:700,
30:175,
31:3000,
32:350,
33:300,
34:3000,
35:3000,
36:300,
37:350,
38:3000,
39:700,
40:800,
41:800,
42:800,
43:700,
44:175,
45:3000,
46:350,
47:300,
48:350,
49:350,
50:350,
51:350,
52:0,
53:350,
54:800,
55:800,
56:800,
57:800,
58:800,
59:800,
60:800,
61:800,
62:800,
63:800,
64:800,
65:800,
66:350,
67:3000,
68:350,
69:350,
70:350,
71:350,
72:350,
73:300,
74:300,
75:300,
76:800,
77:800,
78:800,
79:350,
80:300,
81:800,
82:800,
83:800,
84:300,
85:350,
86:300,
87:350,
88:300,
89:350,
90:800,
91:300,
92:350,
93:300,
94:350,
95:800,
96:175,
97:175,
98:800,
99:175,
100:800,
101:175,
102:175,
103:800,
104:175,
105:175,
106:175,
107:800,
108:175,
109:800,
110:800,
111:800,
112:800,
113:175,
114:800,
115:175,
116:3000,
117:175,
118:800,
119:800,
120:3000,
121:3000,
122:3000,
123:3000,
124:550,
125:550,
126:550,
127:550,
128:550,
129:550,
130:700,
131:700,
132:700,
133:700,
134:700,
135:700,
136:700,
137:700,
138:700,
139:700,
140:3000,
141:700,
142:3000,
143:3000,
144:550,
145:175,
146:175,
147:175,
148:175,
149:175,
150:175,
151:175,
152:175,
153:175,
154:175,
155:175,
156:550,
157:175,
158:700,
159:175,
160:700,
161:175,
162:700,
163:550,
164:550,
165:550,
166:550,
167:550,
168:550,
169:550,
170:550,
171:550,
172:550,
173:550,
174:550,
175:550,
176:550,
177:550,
178:550,
179:550,
180:300,
181:300,
182:300,
183:300,
184:300,
185:300,
186:300,
187:300,
188:300,
189:550,
190:550,
191:550,}
    
    pwmlevel = PWMLookup[channel]
    return pwmlevel
def ctamap():
    Run = rundata() #Initialize the function
    oldchannels =[]
    
    
    while True:
        channels = []
        pwmlevels =[]
       # print (pwmlevels)
        run_stations = Run.master()
    
        for key in run_stations:
            try:
                ledchannel = iomapping(key)
            except KeyError:
                continue
            channels.append(ledchannel)
            
        onlights = list(set(channels).difference(set(oldchannels)))
        
        for i in range(len(onlights)):
            pwmlevels.append(pwmlookup(onlights[i]))
        
        offlights = list(set(oldchannels).difference(set(channels)))
        oldchannels=channels
        
        tlc5947[59] = 0
        for j in range(len(offlights)):
            ('Offlights', offlights[j])
            tlc5947[offlights[j]]=0
            
        for k in range(len(onlights)):
            tlc5947[onlights[k]]=  pwmlevels[k]
            ('Onlights',onlights[k]," .....", pwmlevels[k])
        if offlights and onlights:
            #print (tlc5947[])
            tlc5947.write()
            
        time.sleep(6) #wait 10 seconds - this will get removed and this will be run with a scheduler or as a cron job. 
        
      
            
if __name__ =="__main__": ctamap()

