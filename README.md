# esther-python

## Acquire signals with Red Pitaya board

1. log into Red Pitaya (no pass):  
`ssh root@192.168.10.20`

2. stop network streaming service (If necessary)  
`systemctl stop streaming.service`

3. mount ramdrive (If necessary)  
`mount -o size=128m -t tmpfs none /tmp/stream_files`

3. During shot run  
`./run_acq.sh`

    a. In case you want to run with other parameters:
edit config file if you need more samples, channels,etc.  
`streaming-server -c ./streaming_config_local_ch1_16`

4. Wav Files will be on  
`/tmp/stream_files`

5. Transfer files on main PC:  
 `scp -r root@192.168.10.20:~/data ./`

6. Delete data files on Red Pitaya  
`rm -f /tmp/stream_files/*`

6. in directory esther-python you find python files to convert
to .cvs and to plot .wav files, e.g.  
`python3 data_rp_plot.py data/data_file_2021-07-28_11-49-48`
