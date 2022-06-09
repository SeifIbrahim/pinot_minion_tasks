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

```salt-cp``` is not a suitable for big files or copying a directory. Although you can use some options like ```--chucked``` but it is not guaranteed to work. 
