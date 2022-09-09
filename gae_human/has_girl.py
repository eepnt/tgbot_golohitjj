# serve model
import tensorflow as tf
import numpy as np
import requests

tf.get_logger().setLevel('ERROR')

from tensorflow.python.ops.numpy_ops import np_config
np_config.enable_numpy_behavior()

interpreter = tf.lite.Interpreter(model_path="./model.tflite")
interpreter.allocate_tensors()
output = interpreter.get_output_details()[0]
input = interpreter.get_input_details()[0]

def load_image_into_numpy_array(path):
  image = None
  if(path.startswith('http')):
    resp = requests.get(path)
    image = tf.image.decode_jpeg(np.array(resp.content), channels=3)
  else:
    image_tf = tf.io.read_file(path)
    image = tf.image.decode_jpeg(image_tf, channels=3)

  (w, h, c) = image.shape
  return image.reshape((1, w, h, c)).astype(np.uint8)

# import io
# import PIL.Image
# def load_image_into_numpy_array(path):
#   image = None
#   if(path.startswith('http')):
#     resp = requests.get(path)
#     image = PIL.Image.open(io.BytesIO(resp.content))
#   else:
#     raise("path must start with http")
#   (im_width, im_height) = image.size
#   return np.array(image.getdata()).reshape((1, im_height, im_width, 3)).astype(np.uint8)

def has_girl(path):
    image_np = load_image_into_numpy_array(path)
    image_np_resized = tf.image.resize(image_np, (160, 160))

    interpreter.set_tensor(input['index'], image_np_resized)
    interpreter.invoke()
    result = interpreter.get_tensor(output['index']).item()

    return float(result)

if __name__ == '__main__':
    # true
    print(has_girl('https://assets.burberry.com/is/image/Burberryltd/440338C3-9706-448C-B71E-B2C71D43B4DF?$BBY_V2_ML_1x1$&wid=998&hei=998'))
    # false
    print(has_girl('https://images.unsplash.com/photo-1461800919507-79b16743b257?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8aHVtYW58ZW58MHx8MHx8&w=1000&q=80'))
    # false
    print(has_girl('http://mobileimages.lowes.com/productimages/fcdcacf3-25c8-45bc-b4d3-fb3a96957aa7/10582769.jpg'))
