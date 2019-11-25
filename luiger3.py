import luigi
from datetime import datetime
from trafficGenerator import TrafficMaker as tm
from rawGenerator import RawMaker as rm
from simLauncher import SimLauncher as sm
from csvMaker import CsvMaker
from prePlot import PreparePlot as pp
from chartistLINEstack import LineChartist as ch
from chartist2_LINE import LineChartistSimple as chs
import grouper as gr
from clean import garbageCollector as gc

# contentions = range(5, 30, 5) 
# rawObj = gr.rawDictGen(10, 250, contentions)
contentions = range(50, 500, 50)
rawObj = gr.staticDictGen(50, 500, False, contentions)
plot_xAxis = [0, 550]
simName = "500udp_slots_NonSAT"

# zrobic dla nich + odpowiedni raw object
# byc moze trzeba json config

# 200udpEcho_slots_NonSAT
# 200udp_groups_NonSAT
# 200udp_groups_SAT
# 200udp_slots_NonSAT
# 200udp_slots_SAT

directoryPath = '/home/soczysty7/Mgr19/8LipcaClone/IEEE-802.11ah-ns-3/'
resultsOfSim = '/home/soczysty7/Mgr19/Results/nowyArtNonCSB_4_11/' + simName + '/'
plotDir = '/home/soczysty7/Mgr19/Results/nowyArtNonCSB_4_11/' + simName + '_plots/'
logPath = '/home/soczysty7/Mgr19/Results/nowyArtNonCSB_4_11/' + simName + '_logs/'
subPaths = [str(i) + 'c' for i in contentions]
scriptsDir = '/home/soczysty7/magister_ludi'
#res= '/home/soczysty7/Mgr_2019/Results/testCampaign1toPLOT/'

class Clean(luigi.Task):

    def output(self):
        return luigi.LocalTarget(logPath + '0_collect_garbage.txt')

    def run(self):
        toDelete = 'OptimalRawGroup/'
        cl = gc(directoryPath)
        cl.deleteDirTree(toDelete)
        #cl.deleteDirTree(logPath)

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('posprzatano o: ' + dt_string)

class GenTraffic(luigi.Task):
    
    TrafficPath = 'OptimalRawGroup/traffic/'

    def requires(self):
        return Clean()

    def output(self):
        return luigi.LocalTarget(logPath + '1_traffic-gen.txt')

    def run(self):
        print(rawObj)
        t = 2.25
        o = 0.3
        n = 50
        m = 500
        genTr=tm(directoryPath, self.TrafficPath)
        genTr.genTraffic(n,m,o,t)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('ruch wygenerowany o ' + dt_string)

class GenRawConfigs(luigi.Task):

    def requires(self):
        return GenTraffic()

    def output(self):
        return luigi.LocalTarget(logPath + '2_raw-conf.txt')

    def run(self):
        genRaw = rm(directoryPath,rawObj)
        genRaw.writeCmdsToFile()
        genRaw.generateRawConfigs()

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('RAW configi stworzone o ' + dt_string)

class RunSimulations(luigi.Task):

    def requires(self):
        return GenRawConfigs()

    def output(self):
        return luigi.LocalTarget(logPath + '3_run-sim.txt')

    def run(self):
        simLchrr = sm(directoryPath, resultsOfSim, rawObj, 3) # tu mozna przekazac jsony configi ?
        # simLchrr.writeCmdsToFile()
        simLchrr.RunSimulations("/home/soczysty7/magister_ludi/REMAINING.txt")
        # simLchrr.runRemaining(resultsOfSim)

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('Ukonczono symulacje o  ' + dt_string)

class MakeCsv(luigi.Task):

    # def requires(self):
    #     return RunSimulations()

    def output(self):
        return luigi.LocalTarget(logPath + '4_mk-csvs.txt')

    def run(self):
        analyzer = CsvMaker(resultsOfSim)
        analyzer.transformFolders()
        analyzer.analyzeToCsv(scriptsDir)

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('zrobilem csvki ' + dt_string)

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
            f.write('przygotowano foldery przed zrobieniem wykresow  ' + dt_string)

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
            f.write('Zrobilem wykresy :) ' + dt_string)


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
            f.write('pipeline skonczon ' + dt_string)

# PYTHONPATH='.' luigi --module luiger Final --local-scheduler

# for centralized scheduler mode :
# if __name__ == '__main__':
#    luigi.run(['Final', '--workers', '1'])s