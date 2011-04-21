#!/usr/bin/env python

import sys, time, subprocess, shlex
from daemon import daemon

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

	memory_details_file = open("/tmp/memory_details", "w")
	memory_details_file.write(memory_details_out)
	memory_details_file.close()

def get_load():
	loadfile = open("/proc/loadavg", "r")
	loadavg = loadfile.read()
	loadfile.close()
	loadarray = shlex.split(loadavg.strip())

	load1 = loadarray[0]
	load5 = loadarray[1]
	load15 = loadarray[2]
	numprocs = loadarray[3]

	load_outfile = open ("/tmp/loadavg_details", "w")
	load_outfile.write(loadavg.strip())
	load_outfile.close()

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
	cpufreqs_outfile = open("/tmp/cpufreqs_details", "w")
	cpufreqs_outfile.write(cpufreqs.strip())
	cpufreqs_outfile.close()

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

	cpu_details_file = open("/tmp/cpu_details", "w")
	cpu_details_file.write(cpu_details_out)
	cpu_details_file.close()

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
