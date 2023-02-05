import numpy as np
import matplotlib.pyplot as plt
from barazmoon import BarAzmoon
import json
import numpy as np
import requests
from auto_tuner import AUTO_TUNER_DIRECTORY


with open(f"{AUTO_TUNER_DIRECTORY}/dataset/twitter_trace/workload.txt", "r") as f:
    workload_pattern = f.read()

day = 60 * 60 * 24
# length = 5 * 60
workload_pattern = list(map(int, workload_pattern.split()))
# workload_pattern = workload_pattern[18*length:19*length]
workload_pattern = workload_pattern[15 * day + 80 * 60 : 15 * day + 105 * 60]

workload_pattern = np.array(workload_pattern)


images = list(
    np.load(f"{AUTO_TUNER_DIRECTORY}/experiments/saved_inputs.npy", allow_pickle=True)
)


with open(f"{AUTO_TUNER_DIRECTORY}/experiments/imagenet_idx_to_label.json", "r") as f:
    idx_to_label = json.load(f)


def warmup(url):
    print("Starting warmpu...")
    for i in range(10):
        data = images[np.random.randint(0, 200)]
        requests.post(f"{url}", data=data["data"])
    print("Warmup done.")


def generate_workload(url):

    class WorkloadGenerator(BarAzmoon):
        
        @classmethod
        def get_request_data(cls) -> str:
            image = images[np.random.randint(0, 200)]
            return image["label_code"], image["data"]
        
        @classmethod
        def process_response(cls, data_id: str, response: dict):
            pass
            # print("correct label:", data_id)
                
            # if "error" in response.keys():
            #     print(response["error"])
            # else:
            #     for i in range(len(response["outputs"])):
            #         idx = np.argmax(response["outputs"][i])
            #         # print("predicted label:", idx_to_label[str(idx)])

    
    plt.xlabel("time (seconds)")
    plt.plot(range(1, len(workload_pattern) + 1), workload_pattern, label="request count")
    plt.legend()
    plt.savefig(f"{AUTO_TUNER_DIRECTORY}/../results/workload.png", format="png")
    plt.close()
    print("total number of requests being sent", sum(workload_pattern))
    counter, total_seconds = WorkloadGenerator(workload=workload_pattern, endpoint=url, http_method="post").start()
    print(f"counter: {counter}, total_seconds: {total_seconds}")
    return counter, total_seconds
