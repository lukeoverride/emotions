'''
    Copyright (C) 2017 Luca Surace - University of Calabria, Plymouth University
    
    This file is part of Deemotions. Deemotions is an Emotion Recognition System
    based on Deep Learning method.

    Deemotions is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Deemotions is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Deemotions.  If not, see <http://www.gnu.org/licenses/>.
    
    -----------------------------------------------------------------------

    This file represents the class of the Bayesian Network. It is used to compute posterior probability and
    as merging phase of the whole system.

'''

from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import sys
import csv
import numpy as np


class BayesianNetwork:
    """ This class implement the bayesian network for emotion recognition (positive, negative, neutral)
        based on labels returned by a scene descriptor.
    """

    def __init__(self):
        """Init the object
        """
        pass

    def initModel(self, csv_path, verbose=True):
        """Init the model from a CSV file containing the label and the counting for: positive, negative, neutral

        @param: csv_path the path to the CSV file
        @return True if the model has been correctly initialised, otherwise False.
        """
        self.labels_list = list()
        with open(csv_path, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            is_first_line = True #To jump the header line
            for row in reader:
                if is_first_line:
                    total_positive = float(row[1])
                    total_negative = float(row[2])
                    total_neutral = float(row[3])
                    is_first_line = False
                else:
                    self.labels_list.append(row[0])

        if verbose: print self.labels_list
        # Loading the labels
        positive_vector = np.genfromtxt(csv_path, delimiter=',', skip_header=1, usecols=(1), dtype=np.int32)
        negative_vector = np.genfromtxt(csv_path, delimiter=',', skip_header=1, usecols=(2), dtype=np.int32)
        neutral_vector = np.genfromtxt(csv_path, delimiter=',', skip_header=1, usecols=(3), dtype=np.int32)

        # Generate the connections between the father and the children
        cpd_emotion_node = TabularCPD(variable='emotion_node', variable_card=3, values=[[0.33,0.33,0.33]])

        confusion_matrix_net_153429 = np.array([[470.0,92.0,198.0],
                                                [38.0, 336.0, 130.0],
                                                [46.0, 201.0, 418.0]])
        confusion_matrix_net_153429[0,:] /= np.sum(confusion_matrix_net_153429[0,:])
        confusion_matrix_net_153429[1, :] /= np.sum(confusion_matrix_net_153429[1, :])
        confusion_matrix_net_153429[2, :] /= np.sum(confusion_matrix_net_153429[2, :])

        confusion_matrix_net_171851 = np.array([[583.0,117.0,60.0],
                                                [65.0, 396.0, 43.0],
                                                [149.0, 305.0, 211.0]])
        confusion_matrix_net_171851[0,:] /= np.sum(confusion_matrix_net_171851[0,:])
        confusion_matrix_net_171851[1, :] /= np.sum(confusion_matrix_net_171851[1, :])
        confusion_matrix_net_171851[2, :] /= np.sum(confusion_matrix_net_171851[2, :])



        cpd_cnn_node = TabularCPD(variable='cnn_node', variable_card=3, values=confusion_matrix_net_153429.T,
                                                                                 evidence=['emotion_node'], evidence_card=[3])

        nodes_list = list()
        for label in self.labels_list:
            nodes_list.append(('emotion_node',label))

        nodes_list.append(('emotion_node','cnn_node'))
        self.model = BayesianModel(nodes_list)
        self.model.add_cpds(cpd_emotion_node)
        self.model.add_cpds(cpd_cnn_node)

        cpds_list = list()
        for i in range(len(self.labels_list)):
            p_true_positive = float(positive_vector[i]/total_positive)
            p_true_negative = float(negative_vector[i]/total_negative)
            p_true_neutral = float(neutral_vector[i]/total_neutral)
            p_false_positive = 1.0 - p_true_positive
            p_false_negative = 1.0 - p_true_negative
            p_false_neutral = 1.0 - p_true_neutral 
                      
            cpd_label = TabularCPD(variable=self.labels_list[i], variable_card=2, values=[[p_false_positive, p_false_negative, p_false_neutral], 
                                                                                          [p_true_positive, p_true_negative, p_true_neutral]], 
                                                                                           evidence=['emotion_node'], evidence_card=[3])
            cpds_list.append(cpd_label)
            self.model.add_cpds(cpd_label)
            # print(cpd_label.get_values())
            # print("")

        # Associating the CPDs with the network
        #print("Total CPD: " + str(len(cpds_list)))
        #self.model.add_cpds(cpds_list)
        self.infer = VariableElimination(self.model)
        return self.model.check_model()  # return True if the model is correct


    def inference(self, labels_list):
        """It does the inference using the dictionary passed as input

        @param: labels_list a list of entries: ['carnival', 'festival', 'professional']
            where 1=True and 0=False
        """
        labels_dictionary = {}
        for label in self.labels_list:
            if label in labels_list:
                labels_dictionary[label] = 1
            else:
                labels_dictionary[label] = 0
        posterior = self.infer.query(['emotion_node'], labels_dictionary)
        print(posterior ['emotion_node'])
        return posterior
        
    def returnLabelsListFromNewImage(self, csv_file_row):
        el_num = 0
        toReturn = list()
        for element in csv_file_row:
            if (el_num > 1):
                splitters = csv_file_row[el_num].split("'")
                if (len(splitters) > 1):
                    toReturn.append(splitters[1])
            el_num += 1
        return toReturn

    def inferenceWithCNN(self, labels_list, cnn_pred):
        labels_dictionary = {}
        for label in self.labels_list:
            if label in labels_list:
                labels_dictionary[label] = 1
            else:
                labels_dictionary[label] = 0
        labels_dictionary['cnn_node'] = cnn_pred
        posterior = self.infer.query(['emotion_node'], labels_dictionary)
        return posterior



