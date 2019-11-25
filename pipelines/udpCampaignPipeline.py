import luigi
from datetime import datetime
from utils.trafficGenerator import TrafficMaker as tm
from utils.rawGenerator import RawMaker as rm
from utils.simLauncher import SimLauncher as sm
from utils.csvMaker import CsvMaker
from utils.prePlot import PreparePlot as pp
from utils.chartistLINEstack import LineChartist as ch
import utils.grouper as gr
from utils.clean import garbageCollector as gc

contentions = range(5, 30, 5)
numberOfStations = range(10, 210, 10)
rawObj = gr.staticDictGen(numberOfStations, False, contentions, 1)
plot_xAxis = [0, 210]
trafficDeviation = 0.6
totalTrafficMbps = 3
payloadSize = '1500'
distanceFromAP = '50'
beaconIntervals = ['102400']
simName = "200udpEcho_slots_NonSAT"

outputResultsDir = '/home/soczysty7/Mgr19/Results/STATIC/'
dirWithNS3_ahClone = '/home/soczysty7/Mgr19/8LipcaClone/IEEE-802.11ah-ns-3/'

resultsOfSim = outputResultsDir + simName + '/'
plotDir = outputResultsDir + simName + '_plots/'
logPath = outputResultsDir + simName + '_logs/'
subPaths = [str(i) + 'c' for i in contentions]
scriptsDir = '/home/soczysty7/magister_ludi/analysisScripts'

class Clean(luigi.Task):

    def output(self):
        return luigi.LocalTarget(logPath + '0_collect_garbage.txt')

    def run(self):
        toDelete = 'OptimalRawGroup/'
        cl = gc(dirWithNS3_ahClone)
        cl.deleteDirTree(toDelete)

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('cleaned ' + dt_string)

class GenTraffic(luigi.Task):
    
    TrafficPath = 'OptimalRawGroup/traffic/'

    def requires(self):
        return Clean()

    def output(self):
        return luigi.LocalTarget(logPath + '1_traffic-gen.txt')

    def run(self):
        genTr=tm(dirWithNS3_ahClone, self.TrafficPath)
        genTr.genTraffic(numberOfStations, trafficDeviation, totalTrafficMbps)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('Traffic model generated ' + dt_string)

class GenRawConfigs(luigi.Task):

    def requires(self):
        return GenTraffic()

    def output(self):
        return luigi.LocalTarget(logPath + '2_raw-conf.txt')

    def run(self):
        genRaw = rm(dirWithNS3_ahClone,rawObj, beaconIntervals)
        genRaw.writeCmdsToFile()
        genRaw.generateRawConfigs()

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('RAW configs generated ' + dt_string)

class RunSimulations(luigi.Task):

    def requires(self):
        return GenRawConfigs()

    def output(self):
        return luigi.LocalTarget(logPath + '3_run-sim.txt')

    def run(self):
        simLchrr = sm(dirWithNS3_ahClone, resultsOfSim, rawObj, 
            beaconIntervals,  distanceFromAP, payloadSize, 3)
        simLchrr.writeCmdsToFile()
        simLchrr.RunSimulations()

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('Simulation Completed ' + dt_string)

class MakeCsv(luigi.Task):

    def requires(self):
        return RunSimulations()

    def output(self):
        return luigi.LocalTarget(logPath + '4_mk-csvs.txt')

    def run(self):
        analyzer = CsvMaker(resultsOfSim)
        analyzer.transformFolders()
        analyzer.analyzeToCsv(scriptsDir)

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('Csv created ' + dt_string)

class PrepareToPlot(luigi.Task):

    def requires(self):
        return MakeCsv()

    def output(self):
        return luigi.LocalTarget(logPath + '5_prepare_bf_plot.txt')

    def run(self):
        prep = pp(resultsOfSim, plotDir, rawObj)
        prep.prepareFolders()

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('Prepared dir structure before plotting ' + dt_string)

class GenerateCharts(luigi.Task):

    def requires(self):
        return PrepareToPlot()

    def output(self):
        return luigi.LocalTarget(logPath + '6_make_plots.txt')

    def run(self):
        chartist = ch(plotDir, subPaths, plot_xAxis)
        chartist.makePlotStack()        

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('Charts Generated ' + dt_string)


class Final(luigi.Task):

    def requires(self):
        return GenerateCharts()

    def output(self):
        return luigi.LocalTarget(logPath + '7final.txt')

    def run(self):
        print(rawObj)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('pipeline ended ' + dt_string)

# for centralized scheduler mode :
# if __name__ == '__main__':
#    luigi.run(['Final', '--workers', '1'])s