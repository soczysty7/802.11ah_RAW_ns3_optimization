import luigi
from datetime import datetime
from trafficGenerator import TrafficMaker as tm
from rawGenerator import RawMaker as rm
from simLauncher import SimLauncher as sm
from csvMaker import CsvMaker
from prePlot import PreparePlot as pp
from chartistLINEstack import LineChartist as ch
import grouper as gr

contentions = range(4, 24, 4) 
rawObj = gr.rawDictGen(20, 200, contentions)
plot_xAxis = [10, 210]

directoryPath = "/home/soczysty7/Mgr19/8LipcaClone/IEEE-802.11ah-ns-3/"
resultsOfSim = '/home/soczysty7/Mgr19/Results/tcpecho1/'
plotDir = '/home/soczysty7/Mgr19/Results/tcpecho/'
logPath = '/home/soczysty7/Mgr19/Results/tcpecho1_logs/'
subPaths = [str(i) + 'c' for i in contentions]
scriptsDir = '/home/soczysty7/magister_ludi'

#res= '/home/soczysty7/Mgr_2019/Results/testCampaign1toPLOT/'

class GenTraffic(luigi.Task):
    
    TrafficPath = 'OptimalRawGroup/traffic/'

    def output(self):
        return luigi.LocalTarget(logPath + '1_traffic-gen.txt')

    def run(self):
        print(rawObj)
        t = 3.0
        o = 0.3
        n = 20
        m = 200
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
        simLchrr = sm(directoryPath, resultsOfSim, rawObj, 3)
        simLchrr.writeCmdsToFile()
        simLchrr.RunSimulations()

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        with self.output().open('w') as f:
            f.write('Ukonczono symulacje o  ' + dt_string)

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