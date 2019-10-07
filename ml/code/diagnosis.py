#!/usr/bin/env python
# coding: utf-8

# ### diagnosis.py
# ```
# Created by: Ravi Kasarla
# Creation Date: 02-OCT-2019
# Purpose: Given an lung image, determine if lung has pneumonia 
# Input Parameters:
#     ImageFileFolder
# Output:
#     0 = done not have pneumonia
#     1 = has pneumonia
# Version History:
#     Version          Date            Change Reason
#     -------          ------------    -------------------------------------------------------------------
#     1.1              02-OCT-2019     Initial Creation
# ```

import os
import sys
import keras; print("Keras:" + keras.__version__)
from keras.preprocessing.image import ImageDataGenerator


def dir_file_count(directory):
    return sum([len(files) for r, d, files in os.walk(directory)])


def get_diagnosis(testing_directory):

    # Preprocessing
    # Configure input/ output directory
    # Configure training, validation, testing directory

    print("Current Working Directory:" + os.getcwd())
    print("Directory Passed:" + testing_directory)

    input_directory = r"./ml/data/input/"
    output_directory = r"./ml/data/output/"
    # testing_dir = input_directory + r"test"
    testing_dir = testing_directory
    figure_directory = r"./ml/data/output/figures"

    if not os.path.exists(figure_directory):
        os.mkdir(figure_directory)

    # Image Preprocessing/ Augmentation/ Transformation for Training, Validation, Testing and Dataset
    rescale = 1./255
    target_size = (150, 150)
    batch_size = 163
    class_mode = "categorical"
    # class_mode = "binary"


    test_datagen = ImageDataGenerator(rescale=rescale, data_format='channels_first')

    test_generator = test_datagen.flow_from_directory(
        testing_dir,
        target_size=target_size,
        class_mode=class_mode,
        batch_size=dir_file_count(testing_dir),
        shuffle = False)



    # Test Saved Models
    dir_name = r"./ml/data/output/models/"
    dirs = os.listdir(dir_name)
    for i in range(len(dirs)):
        print(i, dirs[i])


    cur_dir =dir_name+dirs[0]+"/"
    model_names = os.listdir(cur_dir)
    for i in range(len(model_names)):
        print(i, model_names[i])



    model_file = cur_dir+model_names[i]
    print(model_file)

    keras.backend.clear_session()
    model = keras.models.load_model(model_file)

    y_pred = model.predict_generator(test_generator, steps=len(test_generator), verbose=1)  
    y_pred_prob = y_pred[:,0]
    y_pred = y_pred.argmax(axis=-1)
    keras.backend.clear_session()
    print("Y prediction is:" + str(y_pred))
    print("File list is:" + str(test_generator.filenames))
    if sys.platform.startswith('win'):
        fileList = [w.replace('NORMAL\\', '') for w in test_generator.filenames]
    else:
        fileList = [w.replace('NORMAL/', '') for w in test_generator.filenames]
    print("File list is:" + str(fileList))
    retObj = {}
    for i in range(len(fileList)):
        retObj.update({fileList[i] : ["Normal" if y_pred[i] == 0 else "Infected", 
                                      "{:.4%}".format(y_pred_prob[i]) if y_pred[i] == 0 
                                                 else "{:.4%}".format(1-y_pred_prob[i])]})
    
    print("Return Dict:" + str(retObj)) 


    # following is not required; what worked is clear_session before and after predict
    # Heroku is erroring out with memory errors, clear out vaiables
    try:
        del batch_size
        del class_mode
        del cur_dir
        del dir_name
        del dirs
        del figure_directory
        del input_directory
        del model_file
        del model_names
        del output_directory
        del rescale
        del target_size
        del test_datagen
        del test_generator
        del testing_dir
        del y_pred
    except:
        print("Error deleting variables, Warning:" + str(sys.exc_info()[0]))


    return retObj




