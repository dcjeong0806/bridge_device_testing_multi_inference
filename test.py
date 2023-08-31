import psutil , re
results = []
for proc in psutil.process_iter(['pid', 'name', 'username',"cmdline"]):
    if(proc.info["username"] == "ghosti" and proc.info["name"] == "python3"):
        #print(proc.info["cmdline"])
        if(proc.info["cmdline"][1] == "bridge_device_peoplenet_inferencing_manager_each.py"):
            for item in proc.info["cmdline"]:
                print(item)

