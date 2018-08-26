import json
import global_variables as gv

if __name__ == "__main__":
    base_folder = gv.BASE_FOLDER
    patient = "H6"
    experiment = "1"
    complete_folder = base_folder + "//" + patient + "//" + experiment + "//"

    aux = dict()
    aux["wrong_task"] = "tmb"

    with open(complete_folder + "wrong_task_correcao.json", "w") as fp:
        json.dump(aux, fp)