# serve model
import six
import six.moves.urllib.request
import PIL.Image
import tensorflow as tf
import numpy as np

# logging
import logging

tf.get_logger().setLevel('ERROR')

model = tf.keras.models.load_model('./model')

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
    image_np_resized = tf.image.resize(image_np, (160, 160))
    result = model(image_np_resized)

    logging.info({
      "path": path,
      "result": float(result),
    })
    
    return result < 0

if __name__ == '__main__':
    # true
    print(has_human('https://assets.burberry.com/is/image/Burberryltd/440338C3-9706-448C-B71E-B2C71D43B4DF?$BBY_V2_ML_1x1$&wid=998&hei=998'))
    # false
    print(has_human('https://images.unsplash.com/photo-1461800919507-79b16743b257?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8aHVtYW58ZW58MHx8MHx8&w=1000&q=80'))
    # false
    print(has_human('http://mobileimages.lowes.com/productimages/fcdcacf3-25c8-45bc-b4d3-fb3a96957aa7/10582769.jpg'))
