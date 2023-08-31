import json




def main():
    file_path = "./scenemode.json"
    with open(file_path,'r') as f:
        data = json.load(f)
        print(type(data))
        print(len(data))

        for item in data:
            print(item.get('NodeID'))
            print("\n\n")

        '''
        print(data.get("SceneModeID"))
        for item in data.get("Inputs"):
            print(item)
            print("\n\n")

        for item in data.get("Outputs"):
            print(item)
            print("\n\n")

        for item in data.get("Mode"):
            print(item)
            print("\n\n")
        '''

main()