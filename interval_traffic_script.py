#!/usr/bin/env python3
import os
import signal
import subprocess
import threading
import time

SEND_GOLD = [
    'python3', 'send_receive.py', '--mode', 'send', '--iface', 's1-eth1', '--src_ip', '10.0.0.1', '--dst_ip', '10.0.0.3', '--proto', 'tcp', '--threads', '1'
]
RECEIVE_GOLD = [
    'python3', 'send_receive.py', '--mode', 'receive', '--iface', 's1-eth3', '--proto', 'tcp', '--count_bytes'
]

SEND_SILVER = [
    'python3', 'send_receive.py', '--mode', 'send', '--iface', 's1-eth2', '--src_ip', '10.0.0.2', '--dst_ip', '10.0.0.4', '--proto', 'udp', '--threads', '1'
]
RECEIVE_SILVER = [
    'python3', 'send_receive.py', '--mode', 'receive', '--iface', 's1-eth4', '--proto', 'udp', '--count_bytes'
]

CONTROLLER = [
    'python3', 'controller.py'
]

def run_for_interval(cmd, start, end):
    proc_holder = {}
    def target():
        now = time.time() - t0
        if now < start:
            time.sleep(start - now)
        proc = subprocess.Popen(cmd, preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN))
        proc_holder['proc'] = proc
        now = time.time() - t0
        if now < end:
            time.sleep(end - now)
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    thread = threading.Thread(target=target)
    thread.proc_holder = proc_holder
    thread.start()
    return thread

def run_tests(threads, nth_test, gold_traffic, silver_traffic, name):
    time_test = 500
    time_cooldown = 10
    time_warmup = 120
    time_controller = 5

    start_time = nth_test*(time_controller + time_test + time_cooldown)
    end_time = start_time+(time_controller + time_test)

    threads.append(run_for_interval(CONTROLLER, start_time, end_time))
    if gold_traffic:
        threads.append(run_for_interval(RECEIVE_GOLD + [f'--log_file={name}_rec_golden.log'], start_time+time_warmup, start_time+time_test))
        threads.append(run_for_interval(SEND_GOLD, start_time+time_controller, start_time+time_test))
    if silver_traffic:
        threads.append(run_for_interval(RECEIVE_SILVER + [f'--log_file={name}_rec_silver.log'], start_time+time_warmup, start_time+time_test))
        threads.append(run_for_interval(SEND_SILVER, start_time+time_controller, start_time+time_test))

if __name__ == '__main__':
    for log_file in ["reg_history.csv", "mixed_rec_silver.log", "mixed_rec_golden.log", "single_rec_silver.log", "single_rec_golden.log"]:
        try:
            os.remove(log_file)
        except FileNotFoundError:
            pass

    t0 = time.time()
    threads = []

    try:
        run_tests(threads, 0, True, True, 'mixed')
        run_tests(threads, 1, True, False, 'single')
        run_tests(threads, 2, False, True, 'single')

        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("Interrupted! Terminating all processes...")
        for t in threads:
            proc = getattr(t, 'proc_holder', {}).get('proc')
            if proc and proc.poll() is None:
                try:
                    proc.terminate()
                except Exception:
                    pass
        # Optionally, wait for threads to finish cleanup
        for t in threads:
            t.join(timeout=2)
