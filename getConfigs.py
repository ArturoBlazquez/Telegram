import os

def getConfigs(file="config", localFile=True):
    if localFile:
        file = os.path.join(os.path.dirname(__file__), file)
    
    configs=[]
    
    with open(file, 'r') as f:
        for line in f:
            conf=line[:line.find("#")].strip()
            if conf!='':
                configs.append(conf)
    
    if len(configs)==1:
        return configs[0]
    else:
        return configs
