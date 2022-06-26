from multiprocessing import Process
import onnx
from onnx_tf.backend import prepare

versions = [18, 34, 50, 101, 152]

def convert(v):
    onnx_model = onnx.load(f"onnx/resnet{v}-v1-7.onnx")
    tf_rep = prepare(onnx_model, logging_level="DEBUG")
    tf_rep.export_graph(f"tensorflow2/{v}")
    print("Exported version", v)

ps = []
for v in versions:
    p = Process(target=convert, args=(v,))
    p.start()
    ps.append(p)


for proc in ps:
    proc.join()