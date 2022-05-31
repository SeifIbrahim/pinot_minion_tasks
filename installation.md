* ssh myusername@snl-server-3.cs.ucsb.edu
* salt-run manage.up
* salt 'name of device' cmd.run 'linux command'
  * Jaber: raspi-e4:5f:01:56:d9:3a
  * Fahed: raspi-e4:5f:01:56:d5:2b
  * Seif : raspi-e4:5f:01:72:89:99
* salt -N students cmd.run 'linux command' --> runs on all of the pinot nodes
* salt-cp 'raspi-e4:5f:01:72:89:99' test.py /root/
* salt-run jobs.active
* salt -N students saltutil.kill_job <jobid>
* cd does not work so either provide the full path or cd <loc> && <cmd>
*
* Recursive copy does not work so we used git clone
  * git clone https://github.com/SeifIbrahim/pinot_minion_tasks.git --> use the https link instead
* First switch to last mile latency branch 
  * cd pinot_minion_tasks && git checkout last_mile_latency
* pip install -r pinot_minion_tasks/requirements.txt
  ## Installing python 3.10
* apt update &&  apt upgrade -y
* sudo apt install software-properties-common -y
* sudo add-apt-repository ppa:deadsnakes/ppa
* sudo apt install python3.10 -y
* apt install python3.10-distutils -y
* curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
* python3.10 -m pip install -r pinot_minion_tasks/requirements.txt



