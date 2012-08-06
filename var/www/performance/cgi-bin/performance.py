#!/usr/bin/python
from datetime import datetime
import os,sys,re,time,cgi

class Multidict(dict):
	'''Implementation of perl's autovivification feature.
	i.e. if key is not presented - create sub dict'''
	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			value = self[item] = type(self)()
			return value

class FileReader():
	'''Some tools for reading files'''
	def __init__(self):
		self.rootdir="/var/lib/collectd/"
		self.confdir="/etc/performance/"
	def getMachServ(self, filename):
		'''Returns machine and service from given filename'''
		res=re.search(r'%s.+\/(.+)\/(.+)\/.+'%self.rootdir,filename)
		return (res.group(1),res.group(2))
	def getRrdContent(self, filename,day,interval):
		'''Returns multistring with RRD content from given <filename> for <day> days befor now'''
		output="/usr/bin/rrdtool fetch %s MAX -s midnight-%dd -e now-%d-%dd" %(filename,day,int(interval*1.1),day)
		p = os.popen(output,"r")
		output=""
		while 1:
			line = p.readline()
			if not line:
				break
			output+=line
		return output

	def getFilename(self, filename):
		'''Returns short filename from long filename'''
		return re.search(r'.*\/(.+)\.rrd',filename).group(1)

	def readLimits(self):
		'''Returns dict with limits for each metric and each service'''
		try:
			lines=open("%slimits.conf" % self.confdir,"r").readlines()
			limits={}
			metric=""
			for line in lines:
				if line[0]=='>':
					metric=line[1:].strip()
					limits[metric]={}
				else:
					line=line.strip()
					(service,limit)=line.split(" ")
					limits[metric][service]=limit
			return limits
		except:
			print "<br><h1>Troubles with limits.conf</h1>"

	def readMetrics(self):
		'''Returns array of strings - list of metrics'''
		try:
			lines=open("/etc/performance/metrics.conf").readlines()
			lines=map(lambda s: s.strip(), lines)
			return lines
		except:
			print "<br><h1>Configuration file 'metrics' is not found</h1><br>"

	def readServices(self):
		'''Returns dict of services grouped by category'''
		categories={}
		try:
			current=""
			for line in open("%sservices.conf"%self.confdir,"r").readlines():
				if line[0]=='>':
					current=line[1:].strip()
					categories[current]=[]
				else:
					categories[current].append(line.strip())
			return categories
		except:
			return 0

	def readIntervals(self):
		'''Returns tupple (history,interval) - depth of history for rrd files and interval of discretization of measurements'''
		try:
			inters=open("%sintervals.conf"%self.confdir,"r").readlines()
			inters=map(lambda s: s.strip(), inters)
			for inter in inters:
				inter_name,inter_value = inter.split('=')
				if inter_name == "history":
					history=int(inter_value)
				elif inter_name == "interval":
					interval=int(inter_value)
		except:
			interval=3600
			history=7
		return (history,interval)

	def readAllData(self):
		'''Returns multidict of all data for all rrd files in <rootdir> grouped by service, then by machine, then by variable, then by day, and at the end by time'''
		fileList = []
		for root, subFolders, files in os.walk(self.rootdir):
			for file in files:
				fileList.append(os.path.join(root,file))
		allData=Multidict()
		for filename in fileList:
			for day in range(history+1):
				output=self.getRrdContent(filename,day,interval)
				(machine,service)=self.getMachServ(filename)
				vars=output.split("\n")
				keys=vars[0].split()
				output=Multidict()
				for v in vars:
					if re.match(r'(\d+)\:.*',v):
						v="".join(v.split(":")).split()
						for i in range(1,len(keys)+1):
							if v[i] != "-nan":
								output[keys[i-1]][v[0]]=v[i]
				for var in output.keys():
					for tim in output[var].keys():
						variable=self.getFilename(filename)+"/"+var
						if len(output[var][tim]):
							allData[service][machine][variable][day][tim]=output[var][tim]
		return allData

class Data():
	'''Tools for converting data in internal formats'''
	def __init__(self,allData):
		self.allData=allData

	def normalizeTime(self):
		'''Normalize time.
		(replace absolute time (seconds from start of epoch) with relative time (seconds since midnight))'''
		for service in self.allData.keys():
			for machine in self.allData[service].keys():
				for var in self.allData[service][machine].keys():
					for day in self.allData[service][machine][var].keys():
						timesKeys=self.allData[service][machine][var][day].keys()
						timesKeys.sort()
						temp=dict()
						for tim in timesKeys:
							temptime=float(tim)
							midnighttime=time.localtime(temptime)
							midnighttime=time.struct_time((
											midnighttime.tm_year,
											midnighttime.tm_mon,
											midnighttime.tm_mday,
											0, 0, 0,
											midnighttime.tm_wday,
											midnighttime.tm_yday,
											-1))
							temptime-=int(time.mktime(midnighttime))
							temptime=int(temptime)
							temp[temptime]=self.allData[service][machine][var][day][tim]
						del self.allData[service][machine][var][day]
						self.allData[service][machine][var][day]={}
						for tim in temp.keys():
							self.allData[service][machine][var][day][tim]=temp[tim]
						del temp


	def reformatAllData(self):
		'''recreate: allData[service][machine][var][day][tim]
			->
			 allData[var][tim][service][machine][day]'''
		self.newData=Multidict()
		math=Math()
		for service in self.allData.keys():
			for machine in self.allData[service].keys():
				for var in self.allData[service][machine].keys():
					for day in self.allData[service][machine][var].keys():
						diskrTimes={}
						for tim in self.allData[service][machine][var][day].keys():
							if math.getDiskrTime(tim) in diskrTimes.keys(): diskrTimes[math.getDiskrTime(tim)].append(self.allData[service][machine][var][day][tim])
							else: diskrTimes[math.getDiskrTime(tim)]=[self.allData[service][machine][var][day][tim]]
						for tim in sorted(diskrTimes.keys()):
							self.newData[var][tim][service][machine][day]=math.calculateMedian(diskrTimes[tim])
						for tim in self.allData[service][machine][var][day].keys():
							del self.allData[service][machine][var][day][tim]
						del self.allData[service][machine][var][day]
					del self.allData[service][machine][var]
				del self.allData[service][machine]
			del self.allData[service]
		del self.allData

	def calculateAbstractDay(self):
		'''Calculate "abstract day" - day, where value for each time is median by previous days(history)'''
		math=Math()
		for var in self.newData.keys():
			for tim in self.newData[var].keys():
				for service in self.newData[var][tim].keys():
					for machine in self.newData[var][tim][service].keys():
						arr=[self.newData[var][tim][service][machine][day] for day in range(1,history+1) if self.newData[var][tim][service][machine][day]]
						self.newData[var][tim][service][machine]['last']=math.calculateMedian(arr)

	def disposeNewData(self):
		'''Dispose big monstrous multidict with all days'''
		for var in self.newData.keys():
			for tim in self.newData[var].keys():
				for service in self.newData[var][tim].keys():
					for machine in self.newData[var][tim][service].keys():
						for day in self.newData[var][tim][service][machine].keys():
							del self.newData[var][tim][service][machine][day]
						del self.newData[var][tim][service][machine]
					del self.newData[var][tim][service]
				del self.newData[var][tim]
			del self.newData[var]
		del self.newData


	def createTwoDays(self):
		'''Returns multidict with only two days: today and abstract day'''
		self.twoDays=Multidict()
		for var in self.newData.keys():
			for tim in self.newData[var].keys():
				for service in self.newData[var][tim].keys():
					for machine in self.newData[var][tim][service].keys():
						self.twoDays[var][tim][service][machine]['last']=self.newData[var][tim][service][machine]['last']
						self.twoDays[var][tim][service][machine]['today']=self.newData[var][tim][service][machine][0]
		self.disposeNewData()

	def calculateDeltas(self):
		'''Returns table (multidict) with deltas (difference between today value and abstract value)'''
		self.table=Multidict()
		for var in self.twoDays.keys():
			for tim in self.twoDays[var].keys():
				for service in self.twoDays[var][tim].keys():
					for machine in self.twoDays[var][tim][service].keys():
						if ((self.twoDays[var][tim][service][machine]['today']
							or self.twoDays[var][tim][service][machine]['today']==0.0)
						and (self.twoDays[var][tim][service][machine]['last']
							or self.twoDays[var][tim][service][machine]['last']==0.0)):
							self.table[var][tim][service][machine]=float(self.twoDays[var][tim][service][machine]['today'])-float(self.twoDays[var][tim][service][machine]['last'])
						else: self.table[var][tim][service][machine]='nan'


class Beautifier():
	'''Tools for beautify output'''
	def __init__(self):
		self.red="\"#ff0000\""
		self.white="\"#ffffff\""
		self.gray="\"#e0e0e0\""
		self.yellow="\"#ffd89d\""

	def prettyTime(self,tim):
		'''Returns time in standart format HH:MM:SS. Argument must be a time in seconds since midnight(00:00:00)'''
		h=tim//3600
		m=(tim%3600)//60
		s=tim%60
		return "%02d:%02d:%02d" % (h,m,s)

	def beautify(self,measure,value):
		'''Returns value of measure in human-readable format:
		---Bytes,kiloBytes,MegaBytes and GigaBytes for metrics in Bytes
		---units,kilounits,kilokilounits,kilokilokilounits for metrics in units
		---percent for metrics in percent
		---"NO DATA" for metrics without value
		---"Unkn measure" for error in conf file
		Format is described in file metrics.conf:
		0 - Percent
		1 - Bytes
		2 - Units'''
		if value=="nan": return "NO DATA"
		try: value=float(value)
		except TypeError: return "NO DATA"
		if measure==0:
			return "%d%%" % int(value)
		elif measure==1:
			if abs(value/1024)>1:
				value/=1024
				if abs(value/1024)>1:
					value/=1024
					if abs(value/1024)>1:
						value/=1024
						return "%.2fGB" % value
					return "%.2fMB" % value
				return "%.2fKB" % value
			return "%dB" % int(value)
		elif measure==2:
			if abs(value/1000)>1:
				value/=1000
				if abs(value/1000)>1:
					value/=1000
					if abs(value/1000)>1:
						value/=1000
						return "%.2fkkk" % value
					return "%.2fkk" % value
				return "%.2fk" % value
			return "%d" % int(value)
		else:
			return "Unkn %s %.2f" % (measure,value)

	def chooseLimit(self,limits,longmetric,service):
		'''Returns limit value by given metric and service'''
		metric=longmetric.split('/')[0]
		if metric in limits.keys():
			if service in limits[metric].keys():
				return float(limits[metric][service])
			elif "All" in limits[metric].keys():
				return float(limits[metric]["All"])
		return float("+inf")


	def chooseColor(self,metric,limits,lastelem,service,machine,delta):
		'''Returns color for cell in table, by given delta:
		---Red if value will be bigger than limit over 4 history intervals with this delta
		---Yellow if value will be bigger than limit over 8 history intervals with this delta
		---Gray if delta for value is NaN or 0.0
		---White if all right'''
		color=self.white
		if lastelem and (float(lastelem)>0.0):
			last=float(lastelem)
		else: last=0.0
		if (delta and delta!='nan') or delta==0.0:
			limit=self.chooseLimit(limits,metric,service)
			if metric=="http_server_threads_available-value/value":
				if float(delta)*4+last<=limit: color=self.red
				elif float(delta)*8+last<=limit: color=self.yellow
			elif float(delta)*4+last>=limit: color=self.red
			elif float(delta)*8+last>=limit: color=self.yellow
		else: color=self.gray
		return color

class HTMLConstructor():
	'''Tools for construct HTML Page'''
	def __init__(self,twoDays,table):
		self.twoDays=twoDays
		self.table=table

	def printRawTable(self):
		'''Prints data in list without table-formatting'''
		vars=self.table.keys()
		vars.sort()
		for var in vars:
			print var,"<br>"
			tims=self.table[var].keys()
			tims.sort()
			for tim in tims:
				print "&nbsp;",prettyTime(tim),":<br>"
				services=self.table[var][tim].keys()
				services.sort()
				for service in services:
					print "&nbsp;&nbsp;",service,":<br>"
					machines=self.table[var][tim][service].keys()
					machines.sort()
					for machine in machines:
						print "&nbsp;&nbsp;&nbsp;",machine,": ",self.table[var][tim][service][machine],", "
					print "<br>"
				print "<br>"

	def printCategories(self):
		'''Prints categories of services hiddenly (for JavaScript)'''
		fileReader=FileReader()
		categories=fileReader.readServices()
		for cat in sorted(categories.keys()):
			print "<div id='%s' style='display:none'>" % cat
			for service in sorted(categories[cat]):
				print "%s" % service
			print "</div>"

	def printTable(self,metric):
		'''Constructs and prints HTMLTable for given metric'''
		beautifier=Beautifier()
		print "<table id=\"%s\"\n" % metric
		print "<tr id=\"%s_services\">" % metric
		print "<th id=\"%s_tablename\">%s</th>" % (metric,metric)
		widthtim=sorted([(len(self.table[metric][tim]),tim) for tim in sorted(self.table[metric].keys())])[-1][1]
		services=sorted(self.table[metric][widthtim].keys())
		for service in services:
			limit=beautifier.chooseLimit(self.limits,metric,service)
			for machine in sorted(self.table[metric][widthtim][service].keys()):
				print "<th id=\"%s_service_%s\"><span title=\"Limit = %s\">%s</span></th>" % (metric,service,
								beautifier.beautify(int(self.measures[metric]),limit),service)
		print "</tr>\n"
		print "<tr id=\"%s_machines\"><th>Time</th>" % metric
		for service in services:
			for machine in sorted(self.table[metric][widthtim][service].keys()):
				print "<th id=\"%s_machines_%s\">%s</th>" % (metric,machine,machine)
		print "</tr><tbody>"
		times=sorted(self.table[metric].keys())
		for tim in times:
			print "<tr id=\"%s_at_%s\" onmouseover=\"highLight(this,1)\" onmouseout=\"highLight(this,0)\"><th id=\"%s_at_%s_time\" name=\"time\">%s</th>" % (metric,tim,metric,tim,beautifier.prettyTime(tim))
			for service in services:
				for machine in sorted(self.table[metric][widthtim][service].keys()):
					color=beautifier.chooseColor(metric,
									self.limits,
									self.twoDays[metric][tim][service][machine]['today'],
									service,
									machine,
									self.table[metric][tim][service][machine])
					if color=="\"#ff0000\"": name="ERROR"
					elif color=="\"#ffd89d\"": name="WARN"
					elif color=="\"#e0e0e0\"": name="NO_DATA"
					else: name="CELL"
					print "<td name=\"%s\" bgcolor=%s><span title=\"Time: %s\nDelta: %s\">%s</span></td>" % (
												name, color, beautifier.prettyTime(tim),
												beautifier.beautify(int(self.measures[metric]),
													self.table[metric][tim][service][machine]),
												beautifier.beautify(int(self.measures[metric]),
												self.twoDays[metric][tim][service][machine]['today']))
			print "</tr>"
		print "</tbody></table>"

	def Prepare(self):
		'''Initialize arrays and dicts for future. Constructs dict of measure format for each metric.'''
		self.metrics=[]
		self.measures={}
		fileReader=FileReader()
		lines=fileReader.readMetrics()
		for line in lines:
			(a,b)=line.split()
			self.metrics.append(a)
			self.measures[a]=b
		self.limits=fileReader.readLimits()

	def printHTML(self):
		'''Prints big HTML page with tables for each metric'''
		for metric in self.metrics:
			self.printTable(metric)

class Math():
	'''Tools for math calculating'''
	def calculateMedian(self,arr):
		'''Returns median of given array'''
		arr.sort()
		if len(arr)==0: median=0
		elif len(arr)==1: median=arr[0]
		elif len(arr)%2: median=arr[len(arr)//2]
		else: median=(float(arr[len(arr)//2])+float(arr[len(arr)//2-1]))/2
		return median

	def getDiskrTime(self,tim):
		'''Returns discretized time (returns name of interval, in which given time enters'''
		return ((int(tim)//interval+1) if ((int(tim)%interval)>(interval//2)) else (int(tim)//interval))*interval



# def appendTimes(times,elem,tim,var):
	# if times: tims=dict([(t,v) for v,t in times])
	# else: tims={}
	# if tim in tims.keys():
		# if var == "http_server_threads_available-value/value":
			# if elem>tims[tim]: return times
		# elif elem<tims[tim]: return times
	# tims[tim]=elem
	# return [(v,t) for t,v in tims.items()]



# def trim(twoDays):
	# for var in twoDays.keys():
		# times=[]
		# for tim in twoDays[var].keys():
			# for service in twoDays[var][tim].keys():
				# for machine in twoDays[var][tim][service].keys():
					# times=appendTimes(times,twoDays[var][tim][service][machine]['today'],tim,var)
		# times.sort()
		# if var == "http_server_threads_available-value/value": times=times[:3]
		# else: times=times[-3:]
		# times=[t for v,t in times]
		# for tim,v in twoDays[var].items():
			# if tim not in times:
				# twoDays[var].pop(tim)




def main():
	'''Main process of program'''
	global history,interval
	fileReader=FileReader()
	history,interval=fileReader.readIntervals()
	data=Data(fileReader.readAllData())
	data.normalizeTime()
	data.reformatAllData()
	data.calculateAbstractDay()
	data.createTwoDays()
	data.calculateDeltas()
	print "History depth: %s &nbsp;&nbsp;&nbsp; Interval of discretization: %s <br>" % (history,interval)
	print '''<style type="text/css">
	TABLE,TD,TH {
		margin-bottom: 10px;
		border: 1px solid black;
		border-collapse: collapse;
		font-family: arial;
		font-size: 8pt;
	}
	TD,TH {
		padding: 5px;
	}
	TH {
		background-color: #f0f0f0;
	}
	</style>'''
	print '<input type="button" onclick="Category(\'indexes\')" value="Show Indexes">'
	print '<input type="button" onclick="Category(\'fronts\')" value="Show Fronts">'
	print '<input type="button" onclick="Category(\'etc\')" value="Show Etc">'
	print '<input type="button" onclick="Category(\'handlers\')" value="Show Handlers">'
	Builder=HTMLConstructor(data.twoDays,data.table)
	Builder.printCategories()
	Builder.Prepare()
	Builder.printHTML()
	print "</body>"

if __name__=='__main__':
	'''Prints headers'''
	print 'Content-Type: text/html\n\n'
	print '<head>\n\t<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n\t<title>Summary performance ' + datetime.now().strftime("%d-%m-%Y") + '</title>'
	print '<script type="text/javascript" src="filters.js"></script>'
	print "</head><body onLoad=\"joinServices()\">"
	print '<input type="button" onclick="showAll()" value="RESET"><br>'
	print '<input type="button" onclick="showBad()" value="Show Warnings"><br>'
	main()
