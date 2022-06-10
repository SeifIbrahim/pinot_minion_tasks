To see the list of devices, run:

```salt-run manage.up```
 
Choose your targeted devices. If you are going to use only one device, simply use the ID of that node but if you are going to use several devices, you have two options: First one is defining a minion group and choosing a name for that. This method requires special access permits. Then, you can use the following command to run your code on that group:

```salt -N <name of group> cmd.run'<command>'``` 

The second way is using a comma separated list to represent the list of nodes you have.

```salt -L '<first minion>, <second minion> , ...' cmd.run '<command>'```

To copy a file from the server to the minion nodes, you can use:

```salt-cp '<minion name>' <file name> <location in minion>```
 
Usually your default location when you login to the pinot is ```/root/``` but when copy data using ```salt-cp```, it goes to ```/```

You can not use cd command to change directory because there is no ```$HOME``` variable in the PINOT nodes. Instead, you can either use the full path as the argument of command or you can use ```cd <path> && <command>```

```salt-cp``` is not a suitable for big files or copying a directory. Although you can use some options like ```--chucked``` but it is not guaranteed to work. So, we recommend to fetch the codes by git rather than copying from server

Using ssh and running a script to capture many videos is problematic. That’s because the ssh connection to '''snl −server−3''' would be terminated after a while(when you are not inter-
acting with that). When we ran a script on snl −server −3 to run some salt, the script would stop after termination of SSH connection. The solution is using a terminal multiplexer like '''tmux'''. You can run the scrip on '''tmux''' and
it would run it to the end even if the SSH connection is terminated

Our experiment showed that running the script over all of those minions together either by using a list as the argument of salt or using a predefined group of nodes(like $students$) is problematic. We recommend to run the script separately for each minion. In this way, a problem in the execution of the code on one of the minions would not affect the others

You can not easily copy the data from PINOT nodes to the master server or your computer. Initiating the scp communication from a PINOT node to your computer has some problems. Since we do not have interactive terminal with PINOT nodes, we need to use '''SSHPATH'''
to insert the required password. Also, since generating
public keys for the PINOT nodes and using them for
authentication was a pain in the neck(we are so lazy), we
just set up our server in a way that it does not require
public key for granting scp access. For this sake, we used the following commands:
'''sshpass -p "password" rsync -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" -a --ignore-existing "data location on pinot" "the address of your machine(username@IP:location)"'''

