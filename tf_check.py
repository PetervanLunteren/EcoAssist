import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import tensorflow.compat.v1 as tf
print('TensorFlow version:', tf.__version__)
print('tf.test.is_gpu_available:', tf.test.is_gpu_available())