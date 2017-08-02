import cv2
import numpy as np
import tensorflow as tf
import os,sys,glob
from cnn_wildemotion_detection import CnnEmotionDetection
from GoogleDetector import GoogleDetector
from ImagePreprocessing import ImagePreprocessing
from bayesian_network import BayesianNetwork

def classify_image(test_path, image_path,real_label, emotion_detector, google_detector, image_preprocessor, bayes_net):

    targets = ['Positive','Negative','Neutral','Not available']
    reverse_index_list = [0, 2, 1, 3]

    labels = google_detector.detect_labels(image_path)

    with open(image_path, 'rb') as image:
        faces = google_detector.detect_face(image)
        # Reset the file pointer, so we can read the file again
        image.seek(0)
        image_preprocessor.crop_faces(image_path, image, faces)

    image_preprocessor.scale_images(test_path+"Faces/",64.0, image_path)
    emotion_map = emotion_detector.getEmotionMap(test_path+"Scaled/",image_path)
    cnn_predictions = emotion_detector.getMean(emotion_map)
    print cnn_predictions

    if (len(cnn_predictions) > 0):
        predicted_cnn_index = np.argmax(cnn_predictions.values())
        posterior = bayes_net.inferenceWithCNN(labels,reverse_index_list[predicted_cnn_index])
    else:
        predicted_cnn_index = 3
        posterior = bayes_net.inference(labels)
    print predicted_cnn_index
    final_predictions = np.argmax(posterior['emotion_node'].values)
    bayesian_label = targets[final_predictions]


    print image_path
    print "Real label: ",real_label
    if (real_label == bayesian_label):
        print "Bayesian label: ",bayesian_label,
        print "*"
    else:
        print "Bayesian label: ", bayesian_label
    print "CNN label: ",targets[reverse_index_list[predicted_cnn_index]]
    print labels

    #writes files for test
    fd = open(image_path[0:len(image_path) - 4]+".txt", 'a')
    fd.write(str(bayesian_label))
    fd.close()

    return final_predictions




def main(test_path,real_label):
    os.chdir(test_path)

    google_detector = GoogleDetector()
    image_preprocessor = ImagePreprocessing()
    sess = tf.Session()
    emotion_detector = CnnEmotionDetection(sess)
    emotion_detector.load_variables(
        '/home/napster/emotions/wild/checkpoints/emotiW_detection_153429/cnn_emotiW_detection-1499.meta',
        '/home/napster/emotions/wild/checkpoints/emotiW_detection_153429/')
    my_bayes_net = BayesianNetwork()
    is_correct = my_bayes_net.initModel("/home/napster/emotions/wild/wild_GAF_labels_histogram_train_global.csv", False)
    print("Model correct: " + str(is_correct))

    predicted_counter = [0,0,0]
    for image_path in sorted(glob.glob("*")):
        print image_path
        final_predictions = classify_image(test_path, image_path,real_label, emotion_detector, google_detector, image_preprocessor, my_bayes_net)
        predicted_counter[final_predictions] += 1
        print predicted_counter
        print ""



if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])