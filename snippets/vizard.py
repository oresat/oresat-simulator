

import subprocess


vizard_app_path = "/home/monitor/Vizard_Linux/Vizard.x86_64"
vizard_bin_path = "/home/monitor/oresat-simulator/basilisk-sim/_VizFiles/Rose_Sim_UnityViz.bin"
vizard_cmd = [vizard_app_path, "-loadFile", vizard_bin_path]

subprocess.run(vizard_cmd)
