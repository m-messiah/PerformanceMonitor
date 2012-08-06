#!/usr/bin/python
import unittest,copy
import performance
class TestPerformance(unittest.TestCase):
	def setUp(self):
		performance.interval=3600
		performance.history=3
		self.allData={'service_A' : {
					'machine_1' :{
						'metric_X' :{
							0 : {
								1337595000 : 10,
								1337595500 : 10,
								1337596000 : 10,
								1337596500 : 20,
								1337597000 : 20,
								1337597500 : 20,
								1337598000 : 20,
								1337598500 : 20,
								1337599000 : 20,
								1337599500 : 20,
								1337600000 : 40
							},
							1 : {
								1337595000 : 10,
								1337595500 : 10,
								1337596000 : 10,
								1337596500 : 10,
								1337597000 : 10,
								1337597500 : 10,
								1337598000 : 10,
								1337598500 : 10,
								1337599000 : 10,
								1337599500 : 10,
								1337600000 : 10
							},
							2 : {
								1337595000 : 15,
								1337595500 : 15,
								1337596000 : 15,
								1337596500 : 15,
								1337597000 : 15,
								1337597500 : 15,
								1337598000 : 15,
								1337598500 : 15,
								1337599000 : 15,
								1337599500 : 15,
								1337600000 : 15
							},
							3 : {
								1337595000 : 20,
								1337595500 : 20,
								1337596000 : 20,
								1337596500 : 20,
								1337597000 : 20,
								1337597500 : 20,
								1337598000 : 20,
								1337598500 : 20,
								1337599000 : 20,
								1337599500 : 20,
								1337600000 : 20
							},
				
						},	
						'metric_Y' :{
							0 : {
								1337595000 : 4575675,
								1337595500 : 5675675,
								1337596000 : 3675677,
								1337596500 : 3756827,
								1337597000 : 5368563,
								1337597500 : 8356833,
								1337598000 : 2765756,
								1337598500 : 5675675,
								1337599000 : 4536546,
								1337599500 : 5672455,
								1337600000 : 6756725
							},
							1 : {
								1337595000 : 6735765,
								1337595500 : 2565477,
								1337596000 : 7685346,
								1337596500 : 8543546,
								1337597000 : 5473455,
								1337597500 : 7567543,
								1337598000 : 4567375,
								1337598500 : 6756342,
								1337599000 : 4573573,
								1337599500 : 4373567,
								1337600000 : 5675336
							},
						},	
					},
					'machine_2' :{
						'metric_X' :{
							0 : {
								1337595000 : 19,
								1337595500 : 25,
								1337596000 : 34,
								1337596500 : 65,
								1337597000 : 23,
								1337597500 : 56,
								1337598000 : 23,
								1337598500 : 53,
								1337599000 : 22,
								1337599500 : 54,
								1337600000 : 76
							},
							1 : {
								1337595000 : 10,
								1337595500 : 10,
								1337596000 : 10,
								1337596500 : 1,
								1337597000 : 1,
								1337597500 : 1,
								1337598000 : 1,
								1337598500 : 1,
								1337599000 : 1,
								1337599500 : 1,
								1337600000 : 1
							},
							2 : {
								1337595000 : 100,
								1337595500 : 100,
								1337596000 : 100,
								1337596500 : 50,
								1337597000 : 50,
								1337597500 : 50,
								1337598000 : 50,
								1337598500 : 50,
								1337599000 : 50,
								1337599500 : 50,
								1337600000 : 50
							},
							3 : {
								1337595000 : 20,
								1337595500 : 20,
								1337596000 : 20,
								1337596500 : 50,
								1337597000 : 50,
								1337597500 : 50,
								1337598000 : 50,
								1337598500 : 50,
								1337599000 : 50,
								1337599500 : 50,
								1337600000 : 50
							},
						},	
						'metric_Y' :{
							0 : {
								1337595000 : 4364454,
								1337595500 : 4634635,
								1337596000 : 7453347,
								1337596500 : 4563463,
								1337597000 : 4575423,
								1337597500 : 4562544,
								1337598000 : 6574673,
								1337598500 : 4256727,
								1337599000 : 6734735,
								1337599500 : 4764323,
								1337600000 : 4743734
							},
							1 : {
								1337595000 : 4357774,
								1337595500 : 4574574,
								1337596000 : 5747434,
								1337596500 : 5474433,
								1337597000 : 4574734,
								1337597500 : 4573474,
								1337598000 : 4573474,
								1337598500 : 5474745,
								1337599000 : 5477454,
								1337599500 : 4375445,
								1337600000 : 5643554
							},
						},	
					},

			} }
		
	def test_median(self):
		'''calculateMedian'''
		math=performance.Math()
		self.assertEqual(2,math.calculateMedian([2]))
		self.assertEqual(2.5,math.calculateMedian([2,3]))
		self.assertEqual(3.5,math.calculateMedian([1,2,3,4,5,10]))
		self.assertEqual(3,math.calculateMedian([1,2,3,4,5]))
		self.assertEqual(4.5,math.calculateMedian([125,1,2,3,50,4,5,10]))
	def test_getDiskrTime(self):
		'''Time in interval'''
		math=performance.Math()
		self.assertEqual(43200,math.getDiskrTime(43200))
		self.assertEqual(43200,math.getDiskrTime(43000))
		self.assertEqual(43200,math.getDiskrTime(44200))
		self.assertEqual(46800,math.getDiskrTime(45200))
		self.assertEqual(46800,math.getDiskrTime(46799))
		self.assertEqual(39600,math.getDiskrTime(37860))
		
	def test_normalizeTime(self):
		'''Normalize time (relative time from midnight)'''
		oldData=copy.deepcopy(self.allData)
		data=performance.Data(self.allData)
		data.normalizeTime()
		for s in self.allData.keys():
			for m in self.allData[s].keys():
				for v in self.allData[s][m].keys():
					for d in self.allData[s][m][v].keys():
						tims=sorted(oldData[s][m][v][d].keys())
						for i,t in enumerate(sorted(self.allData[s][m][v][d].keys())):
							self.assertEqual(tims[i]-1337544000, t)

	def test_calculateAbstractDay(self):
		'''Calculate Abstract Day'''
		data=performance.Data(self.allData)
		data.normalizeTime()
		data.reformatAllData()
		data.calculateAbstractDay()
		'''Calculate flat data'''
		for tim in sorted(data.newData['metric_X'].keys()):
			self.assertEqual(15, data.newData['metric_X'][tim]['service_A']['machine_1']['last'])
		'''Calculate median with splash'''
		self.assertEqual(20,data.newData['metric_X'][50400]['service_A']['machine_2']['last'])
		'''calculate median with negative splash'''
		self.assertEqual(50,data.newData['metric_X'][54000]['service_A']['machine_2']['last'])
	def test_createRawTable(self):
		'''Calculate Deltas'''
		data=performance.Data(self.allData)
		data.normalizeTime()
		data.reformatAllData()
		data.calculateAbstractDay()
		data.createTwoDays()
		data.calculateDeltas()
		for i,tim in enumerate(sorted(data.table['metric_X'].keys())):
			if i==0:
				self.assertEqual(-5,data.table['metric_X'][tim]['service_A']['machine_1'])
			elif i==1:
				self.assertEqual(5,data.table['metric_X'][tim]['service_A']['machine_1'])
			elif i==2:
				self.assertEqual(25,data.table['metric_X'][tim]['service_A']['machine_1'])
					
	def test_choosecolor(self):
		'''Choose color'''
		data=performance.Data(self.allData)
		data.normalizeTime()
		data.reformatAllData()
		data.calculateAbstractDay()
		data.createTwoDays()
		data.calculateDeltas()
		metric='metric_X'
		measures={}
		measures[metric]=0
		limits={}
		limits[metric]={}
		beautifier=performance.Beautifier()
		limits[metric]['service_A']=80
		'''Usual value'''
		self.assertEqual("\"#ffffff\"" ,beautifier.chooseColor(metric,limits,
											data.twoDays[metric][50400]['service_A']['machine_1']['last'],
											'service_A','machine_1',
											data.table[metric][50400]['service_A']['machine_1']))
		'''NaN value'''
		self.assertEqual("\"#e0e0e0\"" ,beautifier.chooseColor(metric,limits,
											data.twoDays[metric][54000]['service_A']['machine_1']['last'],
											'service_A','machine_1',
											'nan'))
		'''Critical value'''
		self.assertEqual("\"#ff0000\"" ,beautifier.chooseColor(metric,limits,
											data.twoDays[metric][57600]['service_A']['machine_1']['last'],
											'service_A','machine_1',
											data.table[metric][57600]['service_A']['machine_1']))
		

if __name__=="__main__":
	unittest.main()
