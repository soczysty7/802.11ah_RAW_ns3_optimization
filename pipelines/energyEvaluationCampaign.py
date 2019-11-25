import luigi
from datetime import datetime
from utils.trafficGenerator import TrafficMaker as tm
from utils.rawGenerator import RawMaker as rm
from utils.simLauncher import SimLauncher as sm
from utils.csvMaker import CsvMaker
from utils.prePlot import PreparePlot as pp
from utils.chartist2_LINE import LineChartist as ch
import utils.grouper as gr
from utils.clean import garbageCollector as gc

beaconIntervals = ['20480', '40960', '102400', '204800']
contentions = [1, 2, 4]
rawGroups = 2
numberOfStations = [16, 32, 64]
payloadSize = '1500'
distanceFromAP = '25'
totalTrafficMbps = 2
trafficDeviation = 0.3

rawObj = gr.staticDictGen(numberOfStations, False, contentions, rawGroups)
plot_xAxis = [20380, 204700]
simName = 'PS' + payloadSize + '_Rho' + distanceFromAP

dirWithNS3_ahClone = '/home/soczysty7/Mgr19/8LipcaClone/IEEE-802.11ah-ns-3/'
outputResultsDir = '/home/soczysty7/Mgr19/Results/EnergyCampaign3/'

resultsOfSim = outputResultsDir + simName + '/'
#need to do the same for 32 & 64 :
plotDir = outputResultsDir + simName + '_plots/16/'
logPath = outputResultsDir + simName + '_logs/'
subPaths = []
for c in contentions:
    subPaths.append(str(rawGroups) + '_S_' + str(c))
scriptsDir = '/home/soczysty7/magister_ludi/analysisScripts'

currentDirStructures = {}

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
        simLchrr = sm(dirWithNS3_ahClone, resultsOfSim, rawObj, beaconIntervals,  distanceFromAP, payloadSize, 3)
        simLchrr.writeCmdsToFile()
        simLchrr.RunSimulations()

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('Simulation Completed ' + dt_string)

class MakeCsvAndPrepareToPlot(luigi.Task):

    def requires(self):
        return RunSimulations()

    def output(self):
        return luigi.LocalTarget(logPath + '4_mk-csvs.txt')

    def run(self):
        analyzer = CsvMaker(resultsOfSim)
        analyzer.transformNestedTree()
        analyzer.analyzeNestedTree(scriptsDir)
        currentDirStructures = analyzer.getDirStructures()
        prep = pp(resultsOfSim, plotDir, rawObj)
        prep.prepareEnergyCampainDirs(currentDirStructures)

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('Csv created ' + dt_string)

class GenerateCharts(luigi.Task):

    # def requires(self):
    #     return MakeCsvAndPrepareToPlot()

    def output(self):
        return luigi.LocalTarget(logPath + '5_make_plots.txt')

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
        return luigi.LocalTarget(logPath + '6final.txt')

    def run(self):
        print(rawObj)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('pipeline ended ' + dt_string)

# for centralized scheduler mode :
# if __name__ == '__main__':
#    luigi.run(['Final', '--workers', '1'])s