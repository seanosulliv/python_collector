#!/usr/bin/env python

import os, shlex, subprocess, sys, time
from daemon import daemon

hostname = os.uname()[1]
seperator=""
yaketydir = "/tmp/yakety/"

class collector(daemon):
	def run(self):
		while True:
			get_memory()
			get_load()
			get_cpufreqs()
			get_cpuuse()
			time.sleep(60)

def get_memory():
	memory_cmd_args = "/usr/bin/free -b"
	memory_cmd = shlex.split(memory_cmd_args)
	memory_details = subprocess.Popen(memory_cmd, stdout=subprocess.PIPE)
	memory_details_out = memory_details.communicate()[0]
	memory_details_list = shlex.split(memory_details_out.strip())

	memory_total = memory_details_list[7]
	memory_used = memory_details_list[8]
	memory_free = memory_details_list[9]
	memory_shared = memory_details_list[10]
	memory_buffers = memory_details_list[11]
	memory_cached = memory_details_list[12]
	wo_buffers_used = memory_details_list[15]
	wo_buffers_free = memory_details_list[16]
	swap_total = memory_details_list[18]
	swap_used = memory_details_list[19]
	swap_free = memory_details_list[20]

""" Below is if we want to write output to a file
	This will be implemented later - mainly for nagios-type stuff.

	memory_details_outfile = open("/tmp/memory_details", "w")
	memory_details_outfile.write(memory_details_out)
	memory_details_outfile.close()
"""

def get_load():

	stattime = int(time.time())
	yaketyfile_buffer = yaketydir, str(stattime), ".", hostname, ".load"
	yaketyfile = ''.join(yaketyfile_buffer)

	rrd_type = "GAUGE"
	rrd_interval = "60"

	load1 = os.getloadavg()[0]
	load5 = os.getloadavg()[1]
	load15 = os.getloadavg()[2]

	#Write Yaketystats output
	output_load1 = "p=/", hostname, "/load/1-minute", seperator, "t=", rrd_type, seperator, "i=", str(rrd_interval), seperator, "ts=", str(stattime), seperator, "v=", str(load1), "\n"
	output_load5 = "p=/", hostname, "/load/5-minute", seperator, "t=", rrd_type, seperator, "i=", str(rrd_interval), seperator, "ts=", str(stattime), seperator, "v=", str(load5), "\n"
	output_load15 = "p=/", hostname, "/load/15-minute", seperator, "t=", rrd_type, seperator, "i=", str(rrd_interval), seperator, "ts=", str(stattime), seperator, "v=", str(load15), "\n"
	load1_buffer = ''.join(output_load1)
	load5_buffer = ''.join(output_load5)
	load15_buffer = ''.join(output_load15)

	load_outfile = open (yaketyfile, "a")
	load_outfile.write(load1_buffer)
	load_outfile.write(load5_buffer)
	load_outfile.write(load15_buffer)
	load_outfile.close()

""" Below is if we want to write output to a file
	This will be implemented later - mainly for nagios-type stuff.

	load_outfile = open ("/tmp/loadavg_details", "w")
	load_outfile.write(loadavg.strip())
	load_outfile.close()
"""

def get_cpufreqs():
	cpufreqsfile = open("/proc/cpuinfo", "r")
	cpufreqs = cpufreqsfile.read()
	cpufreqsfile.seek(0)
	cpuline = cpufreqsfile.readline()
	cpusplit = cpuline.split()
	while cpusplit[0] != "cpu":
		while cpusplit[1] != "MHz":
			cpuline = cpufreqsfile.readline()
			cpusplit = cpuline.split()

	cpufreqsfile.close()
	cpumhz = cpusplit[3]
	numcpu = cpufreqs.count("cpu MHz")
	cpufreqsarray = shlex.split(cpufreqs.strip())

""" Below is if we want to write output to a file
	This will be implemented later - mainly for nagios-type stuff.

	cpufreqs_outfile = open("/tmp/cpufreqs_details", "w")
	cpufreqs_outfile.write(cpufreqs.strip())
	cpufreqs_outfile.close()
"""

def get_cpuuse():
	cpu_cmd_args = "/usr/bin/sar -u 2 5"
	cpu_cmd = shlex.split(cpu_cmd_args)
	cpu_details = subprocess.Popen(cpu_cmd, stdout=subprocess.PIPE)
	cpu_details_out = cpu_details.communicate()[0]
	cpu_details_list = shlex.split(cpu_details_out.strip())

	cpu_user = cpu_details_list[-5]
	cpu_nice = cpu_details_list[-4]
	cpu_sys = cpu_details_list[-3]
	cpu_iowait = cpu_details_list[-2]
	cpu_idle = cpu_details_list[-1]

""" Below is if we want to write output to a file
	This will be implemented later - mainly for nagios-type stuff.

	cpu_details_outfile = open("/tmp/cpu_details", "w")
	cpu_details_outfile.write(cpu_details_out)
	cpu_details_outfile.close()
"""

if __name__ == "__main__":
	daemon = collector('/tmp/collector.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
