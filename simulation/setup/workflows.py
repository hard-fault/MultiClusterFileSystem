
import os
import sys
import time
import json
from datetime import datetime
from threading import Thread

class SimpleTests:
    def __init__(self, code):
        config = json.load(open("../config/config.json"))
        self.devices = config["devices"]
        self.networks = config["networks"]

        if code == "build":
            print("\n*******************************************************")
            print("\t\tDeploy + Build code on the clients")
            print("*******************************************************")
            self.compileClients()
            print("\n*******************************************************")
            print("\t\tDeploy + Build code on the masters")
            print("*******************************************************")
            self.compileAndStartServers()
        elif code == "run":
            if(len(sys.argv) == 3 and sys.argv[1] == "-r" and sys.argv[2] == "-hdfs"):
                self.hdfsCheck()
            else:
                self.clientWorkflow1()
                self.clientWorkflow2()
                #self.updateFileWorkflow()

    def compileClients(self):
        for d in self.devices["clients"]:
            print("{}".format(d))
            os.system("docker exec -i {} javac FileClient.java".format(d))

    def compileAndStartServers(self):
        started = set()
        for n in self.networks:
            master = self.networks[n]["master"]
            #to make sure the server isn't started twice.
            if master in started:
                continue
            started.add(master)
            print("Starting the server in {}".format(master))
            if master == "mutex_server":
                os.system("docker exec -i {} javac MutexServer.java".format(master))
                os.system("docker exec -d {} java MutexServer".format(master))
            else:
                os.system("docker exec -i {} javac FileServer.java".format(master))
                os.system("docker exec -i {} javac BroadcastListener.java".format(master))
                if(len(sys.argv) == 3 and sys.argv[1] == "-b" and sys.argv[2] == "-hdfs"):
                    os.system("docker exec -d {} java FileServer hdfs".format(master))
                else:
                    os.system("docker exec -d {} java FileServer".format(master))
                os.system("docker exec -d {} java BroadcastListener".format(master))

    """
    File created by a client in cluster1 is accessible by a client in cluster2
    """
    def clientWorkflow1(self):
        startTime = datetime.now()
        print("\n\n\tWORKFLOW-1")
        print("\t----------\n")
        print("(C1.1 writes files, C2.1 reads the files)")
        # C1.1 write 5 files to it's master1
        commands = [
            "docker exec -i C1.1 touch C1.1_file1.txt",
            "docker exec -i C1.1 touch C1.1_file2.txt",
            "docker exec -i C1.1 touch C1.1_file3.txt",
            "docker exec -i C1.1 touch C1.1_file4.txt",
            "docker exec -i C1.1 touch C1.1_file5.txt",
            "docker exec -i C1.1 java FileClient snd C1.1_file1.txt",
            "docker exec -i C1.1 java FileClient snd C1.1_file2.txt",
            "docker exec -i C1.1 java FileClient snd C1.1_file3.txt",
            "docker exec -i C1.1 java FileClient snd C1.1_file4.txt",
            "docker exec -i C1.1 java FileClient snd C1.1_file5.txt",
        ]
        print("\tC1.1 WRITES")
        print("\t************")
        for command in commands:
            os.system(command)

        #Another cluster client request and recieves files
        commands= [
            "docker exec -i C2.1 java FileClient rcv r C1.1_file1.txt",
            "docker exec -i C2.1 java FileClient rcv r C1.1_file2.txt",
            "docker exec -i C2.1 java FileClient rcv r C1.1_file3.txt",
            "docker exec -i C2.1 java FileClient rcv r C1.1_file4.txt",
            "docker exec -i C2.1 java FileClient rcv r C1.1_file5.txt",
        ]

        print("\tC2.1 READS")
        print("\t************")
        for command in commands:
            os.system(command)

        print("\n\tC2.1(ls output)")
        os.system("docker exec -i C2.1 ls | grep txt")

        commands= [
            "docker exec -i {} rm C1.1_file1.txt",
            "docker exec -i {} rm C1.1_file2.txt",
            "docker exec -i {} rm C1.1_file3.txt",
            "docker exec -i {} rm C1.1_file4.txt",
            "docker exec -i {} rm C1.1_file5.txt",
        ]
        for command in commands:
            os.system(command.format("C1.1"))
            os.system(command.format("C2.1"))

        endTime = datetime.now()
        print("\n###Time taken: {}\n\n\n".format(endTime - startTime))

    """
    All clusters are interconnected. All create one file each. All can access each other's files.
    """
    def clientWorkflow2(self):
        startTime = datetime.now()
        print("\n\n\tWORKFLOW-2")
        print("\t----------\n")
        print("(All Clients write and read each other's files.)")
        # All clients create and send a file to the master
        print("\n\nALL CLIENTS WRITE A FILE\n")
        for d in self.devices["clients"]:
            print("\t{} WRITES".format(d))
            print("\t************")
            os.system("docker exec -i {0} touch {0}_file.txt".format(d))
            os.system("docker exec -i {0} java FileClient snd {0}_file.txt".format(d))
            time.sleep(0.5)

        # All clients request each other's files
        print("\n\n\n\nALL CLIENTS READ EACH OTHER'S FILES")
        for d in self.devices["clients"]:
            print("\n\t{} READS".format(d))
            print("\t************")
            for fileName in self.devices["clients"]:
                os.system("docker exec -i {0} java FileClient rcv r {1}_file.txt".format(d, fileName))
                time.sleep(0.5)
            print("\t{}(ls output)".format(d))
            os.system("docker exec -i {} ls | grep txt".format(d))

        #Delete the files
        for d in self.devices["clients"]:
            for fileName in self.devices["clients"]:
                os.system("docker exec -i {0} rm {1}_file.txt".format(d, fileName))
        endTime = datetime.now()
        print("\n####Time taken: {}\n\n\n".format(endTime - startTime))

    def updateFileWorkflow (self):

        commands = [

            # print "Files in C1.1: "
            "docker exec -i C1.1 ls | grep txt",

            # C1.1 write 1 file c1.1_file6.txt to it's master1
            "docker exec -i C1.1 touch c1.1_file6.txt",

            #Send the file to it's cluster master
            "docker exec -i C1.1 java FileClient snd c1.1_file6.txt",

            #All other cluster's client request and receives files
            "docker exec -i C2.1 java FileClient rcv r c1.1_file6.txt",
            "docker exec -i C3.1 java FileClient rcv r c1.1_file6.txt",

            #Verify if the file rcvd successfully.
            # print "List files in C2.1"
            "docker exec -i C2.1 ls | grep txt",

            # print "List files in C3.1"
            "docker exec -i C3.1 ls | grep txt",

            # print "C2.1 requests the file c1.1_file6.txt to write"
            "docker exec -i C2.1 java FileClient rcv w c1.1_file6.txt",

            # print "At the same time c3.1 also requests for the same"
            "docker exec -i C3.1 java FileClient rcv w c1.1_file6.txt",
            ]

        for command in commands:
            os.system(command)

    def hdfsCheck(self):
        self.clientWorkflow1()
        return


if len(sys.argv) >= 2 and sys.argv[1] == "-b":
    SimpleTests("build")
elif len(sys.argv) >= 2 and sys.argv[1] == "-r":
    SimpleTests("run")
else:
    print "Use [-b to build] or [-b -hdfs to build hdfs] or [-r to run]"











