"""Keras Tuner tool lab and 8 genuine VisionGuard trials.

Uses built-in sklearn digits dataset for offline toy lab (no Fashion-MNIST network download).
"""
from __future__ import annotations
import csv
import os
import sys
from pathlib import Path
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL','2')
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'
OUT.mkdir(exist_ok=True)
import numpy as np
import tensorflow as tf
import keras_tuner as kt
import mlflow
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

sys.path.insert(0,str(ROOT/'scripts'))
from train_models import pipeline


def local_mlflow():
    (ROOT/'mlruns').mkdir(exist_ok=True)
    mlflow.set_tracking_uri('sqlite:///mlflow.db')
    mlflow.set_experiment('L230558_A2_Ops_VisionGuard')


def toy_tune():
    digits=load_digits()
    X=digits.data.astype('float32')/16
    y=(digits.target>=5).astype('float32')
    a,b,ya,yb=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
    def build(hp):
        mod=tf.keras.Sequential([tf.keras.Input(shape=(64,)),
            tf.keras.layers.Dense(hp.Choice('units',[16,32,64]),activation='relu'),
            tf.keras.layers.Dense(1,activation='sigmoid')])
        mod.compile(optimizer=tf.keras.optimizers.Adam(hp.Choice('lr',[1e-3,1e-2])),
                    loss='binary_crossentropy',metrics=['accuracy'])
        return mod
    tuner=kt.RandomSearch(build,objective='val_accuracy',max_trials=3,overwrite=True,
               directory=str(OUT/'tuner_cache'),project_name='built_in_digits_toy',seed=42)
    tuner.search(a,ya,validation_data=(b,yb),epochs=2,batch_size=64,verbose=0)
    res=[]
    for t in tuner.oracle.trials.values():
        res.append({'id':t.trial_id,'status':t.status,'score':t.score,**t.hyperparameters.values})
    path=OUT/'toy_tuner_results.csv'
    with path.open('w',newline='',encoding='utf-8') as fh:
        fields=sorted(set().union(*(r.keys() for r in res)))
        writer=csv.DictWriter(fh,fieldnames=fields);writer.writeheader();writer.writerows(res)
    print('TOY TUNER:',len(res),'trials. Saved',path)
    with mlflow.start_run(run_name='toy_keras_tuner_digits'):
        mlflow.set_tag('tool_lab','KerasTuner RandomSearch using built-in sklearn digits')
        mlflow.log_artifact(str(path))
        mlflow.log_metric('toy_trials_executed',len(res))


def real_tune():
    train=pipeline('train',shuffle=True)
    val=pipeline('val')

    def build(hp):
        # Keras tuner explores dropout, learning rate, and unfrozen backbone count.
        # MobileNetV2 alpha .35 matches the existing trained transfer model.
        inp=tf.keras.Input(shape=(128,128,3))
        x=tf.keras.layers.Rescaling(1/127.5,offset=-1)(inp)
        backbone=tf.keras.applications.MobileNetV2(input_shape=(128,128,3),alpha=.35,
                                                    weights='imagenet',include_top=False)
        unfreeze=hp.Choice('unfrozen_last_layers',[0,10,20])
        backbone.trainable=unfreeze>0
        for layer in backbone.layers:
            layer.trainable=False
        if unfreeze>0:
            for layer in backbone.layers[-unfreeze:]:
                layer.trainable = not isinstance(layer,tf.keras.layers.BatchNormalization)
        x=backbone(x,training=False)
        x=tf.keras.layers.GlobalAveragePooling2D()(x)
        x=tf.keras.layers.Dropout(hp.Choice('dropout',[0.20,0.40]))(x)
        out=tf.keras.layers.Dense(1,activation='sigmoid')(x)
        model=tf.keras.Model(inp,out)
        lr=hp.Choice('learning_rate',[1e-4,3e-5])
        model.compile(optimizer=tf.keras.optimizers.Adam(lr),
                      loss=tf.keras.losses.BinaryCrossentropy(),
                      metrics=['accuracy'])
        return model
    tuner=kt.RandomSearch(build,objective='val_accuracy',max_trials=8,overwrite=True,
                     directory=str(OUT/'tuner_cache'),project_name='visionguard_8_trials',seed=42)
    tuner.search(train,validation_data=val,epochs=2,verbose=2,
                 callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss',patience=1)])
    results=[]
    for t in tuner.oracle.trials.values():
        item={'trial':t.trial_id,'status':t.status,
              'validation_accuracy':float(t.score) if t.score is not None else '',
              **t.hyperparameters.values}
        results.append(item)
    path=OUT/'tuning_results.csv'
    with path.open('w',newline='',encoding='utf-8') as fo:
        fields=['trial','status','validation_accuracy','unfrozen_last_layers','dropout','learning_rate']
        w=csv.DictWriter(fo,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(results)
    print('REAL TUNER: total completed:',sum(x['status']=='COMPLETED' for x in results),'of 8')
    print('Saved',path)
    for r in results:
        if r['status']!='COMPLETED':continue
        with mlflow.start_run(run_name='tuner_trial_'+str(r['trial'])):
            mlflow.set_tags({'run_origin':'real_KerasTuner_trial',
                             'training_epochs':'2', 'data_version':'DVC data/raw.dvc'})
            mlflow.log_params({k:v for k,v in r.items() if k not in ('trial','status','validation_accuracy')})
            mlflow.log_metric('validation_accuracy',r['validation_accuracy'])
            mlflow.log_artifact(str(path))
    if any(r['status']!='COMPLETED' for r in results):
        print('WARNING: Not all trials finished. Inspect output; do not claim 8 completed.')


if __name__=='__main__':
    local_mlflow()
    tf.keras.utils.set_random_seed(42)
    toy_tune()
    real_tune()
