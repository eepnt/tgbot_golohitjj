# serve model
import six
import six.moves.urllib.request
import PIL.Image
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

# logging
import logging

tf.get_logger().setLevel('ERROR')

model_name = 'SSD MobileNet V2 FPNLite 320x320'
model_handle = 'https://tfhub.dev/tensorflow/ssd_mobilenet_v2/fpnlite_320x320/1'
hub_model = hub.load(model_handle)

def load_image_into_numpy_array(path):
  image = None
  if(path.startswith('http') or path.startswith('https')):
    response = six.moves.urllib.request.urlopen(path)
    image_data = response.read()
    image_data = six.BytesIO(image_data)
    image = PIL.Image.open(image_data)
  else:
    image_data = tf.io.gfile.GFile(path, 'rb').read()
    image = PIL.Image.open(six.BytesIO(image_data))

  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (1, im_height, im_width, 3)).astype(np.uint8)

def has_human(path):
    image_np = load_image_into_numpy_array(path)
    results = hub_model(image_np)
    result = {key:value.numpy() for key,value in results.items()}
    label_id_offset = 0
    rt = [ 
        {
            'index': index,
            'box': result['detection_boxes'][0][index],
            'obj': i,
            'score': result['detection_scores'][0][index],
        } for index, i in enumerate((result['detection_classes'][0] + label_id_offset).astype(int))
    ]
    logging.info(rt)
    
    found = False
    # id 1 = human. ref:
    # https://github.com/tensorflow/models/blob/master/research/object_detection/data/mscoco_label_map.pbtxt
    for i in filter(lambda x: x['obj'] == 1, rt):
        if i['score'] > 0.5:
            found = True
            break
    return found

if __name__ == '__main__':
    # true
    print(has_human('https://images.unsplash.com/photo-1461800919507-79b16743b257?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8aHVtYW58ZW58MHx8MHx8&w=1000&q=80'))
    # false
    print(has_human('http://mobileimages.lowes.com/productimages/fcdcacf3-25c8-45bc-b4d3-fb3a96957aa7/10582769.jpg'))
