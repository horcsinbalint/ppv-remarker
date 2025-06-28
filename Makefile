.PHONY: start_switches run_simulation plot plot_pdf plot_minimum_ppv controller

# generate switch configuration and start the network
start_switches:
	python3 script_generator.py
	sudo python3 network.py

# run traffic simulation
run_simulation:
	sudo python3 interval_traffic_script.py

# plot data rates
plot:
	python3 plot_data_rate.py single_rec_golden.log single_rec_silver.log mixed_rec_golden.log mixed_rec_silver.log

# plot data rates and save as PDF
plot_pdf:
	python3 plot_data_rate.py single_rec_golden.log single_rec_silver.log mixed_rec_golden.log mixed_rec_silver.log --pdf

# plot minimum packets per value (PPV)
plot_minimum_ppv:
	python3 plot_minimum_ppv.py

# start the controller
controller:
	sudo python3 controller.py