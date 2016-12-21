import logging

import qnd
import tensorflow as tf



logging.getLogger().setLevel(logging.INFO)

qnd.add_flag("--batch_size", type=int, default=64)
qnd.add_flag("--batch_queue_capacity", type=int, default=1024)



def read_file(filename_queue):
  _, serialized = tf.TFRecordReader().read(filename_queue)

  scalar_feature = lambda dtype: tf.FixedLenFeature([], dtype)

  features = tf.parse_single_example(serialized, {
    "image_raw": scalar_feature(tf.string),
    "label": scalar_feature(tf.int64),
  })

  image = tf.decode_raw(features["image_raw"], tf.uint8)
  image.set_shape([28**2])

  return tf.train.shuffle_batch(
      [tf.to_float(image) / 255 - 0.5, features["label"]],
      batch_size=qnd.FLAGS.batch_size,
      capacity=qnd.FLAGS.batch_queue_capacity,
      min_after_dequeue=qnd.FLAGS.batch_queue_capacity//2)


def linear(h, num_outputs):
  return tf.contrib.layers.fully_connected(
      h,
      num_outputs=num_outputs)


def minimize(loss):
  return tf.contrib.layers.optimize_loss(
      loss,
      tf.contrib.framework.get_global_step(),
      0.01,
      "Adam")


def mnist_model(image, number):
  h = linear(image, num_outputs=42)
  h = linear(h, num_outputs=10)
  loss = tf.reduce_mean(
      tf.nn.sparse_softmax_cross_entropy_with_logits(h, number))

  return tf.argmax(h, axis=1), loss, minimize(loss)


run = qnd.def_run()


def main():
  run(mnist_model, read_file)



if __name__ == "__main__":
  main()
