"""VisionGuard Step 3: genuine local MLflow demo, historical import, extra tracked runs, and DagsHub sync.

Never claim historical imports were logged live. Local file-backed tracking; DagsHub uses .env secrets.
"""
from __future__ import annotations
import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'
MODELS = ROOT / 'models'

import numpy as np
import mlflow

EXPERIMENT = 'L230558_A2_Ops_VisionGuard'


def configure(local=True):
    if local:
        # MLflow 3.x needs a supported database-backed tracking store.
        # The batch scripts run from ROOT, so both training and UI use the same DB.
        mlflow.set_tracking_uri('sqlite:///mlflow.db')
    else:
        from dotenv import load_dotenv
        load_dotenv(ROOT / '.env', override=False)
        required = ['MLFLOW_TRACKING_URI', 'MLFLOW_TRACKING_USERNAME', 'MLFLOW_TRACKING_PASSWORD']
        missing = [k for k in required if not os.getenv(k)]
        if missing:
            raise RuntimeError('Missing DagsHub credentials from .env: ' + ', '.join(missing))
        if '.mlflow' not in os.getenv('MLFLOW_TRACKING_URI', ''):
            raise RuntimeError('Tracking URI should end in .mlflow (DagsHub repository).')
        mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
    mlflow.set_experiment(EXPERIMENT)
    print('Tracking URI:', mlflow.get_tracking_uri(), flush=True)


def json_load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def maybe_log_file(p, artifact_path=None):
    p = Path(p)
    if p.exists() and p.is_file():
        mlflow.log_artifact(str(p), artifact_path=artifact_path)


def training_history_run(prefix, base_params, remote=False):
    mh = OUT / (prefix + '_metrics.json')
    hh = OUT / (prefix + '_history.json')
    if not (mh.exists() and hh.exists()):
        print('SKIP historical', prefix, 'missing real outputs')
        return False
    met = json_load(mh)
    history = json_load(hh)
    with mlflow.start_run(run_name='step2_' + prefix):
        mlflow.set_tags({'project':'VisionGuard','data_version':'DVC data/raw.dvc','seed':'42',
                         'run_origin':'imported_from_step2_outputs',
                         'run_type':'historical_import_not_live_autologged'})
        mlflow.log_params({**base_params, 'approach':prefix})
        for key, values in history.items():
            for ep, value in enumerate(values, 1):
                mlflow.log_metric(key, float(value), step=ep)
        for key, value in met.items():
            if isinstance(value, (int, float)):
                mlflow.log_metric('test_' + key if key not in ('validation_f1','threshold_from_validation') else key, float(value))
        for item in (mh, hh, OUT / (prefix + '_curves.png'), OUT / (prefix + '_roc.png'),
                     OUT / (prefix + '_confusion_matrix.png'), OUT / (prefix + '_model_summary.txt'),
                     OUT / (prefix + '_misclassified.png')):
            maybe_log_file(item, 'outputs')
        for sp in ('train','val','test'):
            maybe_log_file(OUT / f'{sp}_split.csv', 'splits')
        maybe_log_file(OUT / 'pip_freeze.txt', 'environment')
        model = MODELS / (prefix + '.keras')
        if prefix == 'transfer_head': model = MODELS / 'transfer_head.keras'
        if model.exists():
            maybe_log_file(model, 'keras_checkpoints')
    print('Logged actual historical outputs:', prefix)
    return True


def toy_runs():
    from sklearn.datasets import load_digits
    from sklearn.model_selection import train_test_split
    import tensorflow as tf
    from matplotlib import pyplot as plt
    tf.keras.utils.set_random_seed(42)
    d = load_digits()
    x = d.data.astype('float32') / 16.0
    y = (d.target >= 5).astype('float32')
    xtr, xv, ytr, yv = train_test_split(x,y,test_size=.20,stratify=y,random_state=42)
    for i, lr in enumerate((1e-3, 2e-3),1):
        tf.keras.backend.clear_session()
        model = tf.keras.Sequential([tf.keras.Input(shape=(64,)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')])
        model.compile(optimizer=tf.keras.optimizers.Adam(lr),loss='binary_crossentropy',metrics=['accuracy'])
        class Manual(tf.keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                for key, value in (logs or {}).items():
                    mlflow.log_metric(key, float(value),step=epoch+1)
        with mlflow.start_run(run_name=f'toy_digits_lr_{lr:g}'):
            mlflow.log_params({'dataset':'sklearn built-in digits', 'learning_rate':lr,
                              'epochs':3,'units':32,'seed':42,'model':'tiny Keras binary MLP'})
            h = model.fit(xtr,ytr,validation_data=(xv,yv),epochs=3,batch_size=64,
                          callbacks=[Manual()],verbose=0)
            fig, ax = plt.subplots(figsize=(6,3))
            ax.plot(h.history['loss'],label='training loss')
            ax.plot(h.history['val_loss'],label='validation loss')
            ax.legend(); ax.set_xlabel('Epoch'); fig.tight_layout()
            png=OUT/f'toy_digits_lr_{i}_loss.png'; fig.savefig(png,dpi=130);plt.close(fig)
            mlflow.log_artifact(str(png))
            filepath=OUT/f'toy_digits_lr_{i}.keras'; model.save(filepath)
            mlflow.log_artifact(str(filepath), 'toy_model_file')
            print(f'TOY {i}: val_accuracy {h.history["val_accuracy"][-1]:.4f}')


def run_local():
    configure(local=True)
    toy_runs()
    import_args={'image_size':128,'batch_size':16,'epochs':'6 baseline / 4 head / 3 fine',
                 'optimizer':'Adam','labels':'Real=0, AI-generated=1'}
    ct=0
    for prefix in ('baseline','transfer_head','transfer_finetuned'):
        ct += training_history_run(prefix,import_args)
    print(f'SUCCESS local MLflow: {ct} actual historical runs + 2 genuine toy runs.')
    print('For at least six VisionGuard runs, run 08_THREE_NEW_RUNS.bat.')


def new_runs():
    configure(local=True)
    import tensorflow as tf
    sys.path.insert(0,str(ROOT/'scripts'))
    from train_models import baseline_model, pipeline, records, probabilities
    from sklearn.metrics import f1_score
    from matplotlib import pyplot as plt
    tf.keras.utils.set_random_seed(42)
    _, yval = records('val')
    train = pipeline('train',shuffle=True)
    val = pipeline('val')
    results=[]
    for i, lr in enumerate((0.0005,0.0002,0.00005),start=1):
        tf.keras.backend.clear_session()
        tf.keras.utils.set_random_seed(42+i)
        model=baseline_model()
        model.compile(optimizer=tf.keras.optimizers.Adam(lr), loss='binary_crossentropy',
                      metrics=[tf.keras.metrics.BinaryAccuracy(name='accuracy'),tf.keras.metrics.AUC(name='auc')])
        # Genuine live tracking. On the last experiment, also demonstrate MLflow autologging.
        use_auto=(i==3)
        if use_auto:
            try:
                mlflow.tensorflow.autolog(log_models=False,disable=False)
                print('MLflow TensorFlow autologging ENABLED for experiment 3')
            except Exception as exc:
                print('Autolog unavailable, continuing manual:',exc)
                use_auto=False
        class Manual(tf.keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                for k,v in (logs or {}).items(): mlflow.log_metric(k,float(v),step=epoch+1)
        with mlflow.start_run(run_name=f'baseline_live_lr_{lr:g}'):
            mlflow.set_tags({'project':'VisionGuard','run_origin':'live_training','seed':str(42+i),
                             'logging_mode':'tensorflow_autolog' if use_auto else 'manual_keras_callback',
                             'data_version':'DVC data/raw.dvc'})
            mlflow.log_params({'model':'custom_CNN','learning_rate':lr,'batch_size':16,
                              'image_size':128,'epochs':2,'dropout':0.35,'seed':42+i})
            h=model.fit(train,validation_data=val,epochs=2,verbose=2,callbacks=[Manual()])
            p=probabilities(model,val)
            val_f1=float(f1_score(yval,p>=0.5,zero_division=0))
            mlflow.log_metric('validation_f1_at_0_5',val_f1)
            plt.figure(figsize=(6,3));plt.plot(h.history['loss'],label='train');
            plt.plot(h.history['val_loss'],label='val');plt.legend();plt.tight_layout()
            artifact=OUT/f'live_lr_{i}_curves.png';plt.savefig(artifact,dpi=130);plt.close()
            mlflow.log_artifact(str(artifact))
            results.append({'run':f'baseline_live_lr_{lr:g}','lr':lr,'val_accuracy':h.history['val_accuracy'][-1],
                            'val_f1_at_0.5':val_f1})
        if use_auto:
            try:mlflow.tensorflow.autolog(disable=True)
            except Exception: pass
        print('LIVE RUN',i,'val F1',val_f1)
    path=OUT/'extra_experiments.csv'
    with path.open('w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=results[0]);w.writeheader();w.writerows(results)
    print('SUCCESS: 3 real extra VisionGuard configurations tracked LIVE; results',path)


def remote_sync():
    global mlflow
    configure(local=False)
    base={'image_size':128,'batch_size':16,'seed':42,'labels':'Real=0,AI-generated=1'}
    for prefix in ():
        training_history_run(prefix,base,True)
    for csvname in ('extra_experiments.csv','tuning_results.csv'):
        f=OUT/csvname
        if not f.exists():continue
        with f.open(newline='',encoding='utf-8') as fo: rows=list(csv.DictReader(fo))
        for i,row in enumerate(rows):
            with mlflow.start_run(run_name=('remote_import_'+csvname.replace('.csv','')+'_'+str(i+1))):
                mlflow.set_tag('run_origin','imported_from_recorded_local_result_not_live')
                for k,v in row.items():
                    try:mlflow.log_metric(k,float(v))
                    except (ValueError,TypeError):mlflow.log_param(k,str(v)[:250])
                mlflow.log_artifact(str(f))
        print('Synced:', csvname,len(rows))
    # Register two genuinely different checkpoints, when the server supports registry.
    if all((MODELS/f).exists() for f in ('baseline.keras','champion.keras')):
        try:
            import tensorflow as tf
            import mlflow.keras
            for mfile, name in (('baseline.keras','baseline'),('champion.keras','champion')):
                with mlflow.start_run(run_name='register_'+name):
                    model=tf.keras.models.load_model(MODELS/mfile)
                    info=mlflow.keras.log_model(model,name=name,
                        registered_model_name='L230558_A2_Ops_VisionGuard',
                        pip_requirements=['tensorflow>=2.18,<2.22'])
                    print('Registered',name,'at',info.model_uri)
            client=mlflow.MlflowClient()
            versions=client.search_model_versions("name='L230558_A2_Ops_VisionGuard'")
            if len(versions)>=2:
                latest=max(versions,key=lambda x:int(x.version))
                client.set_registered_model_alias('L230558_A2_Ops_VisionGuard','champion',latest.version)
                print('Registry alias champion -> version', latest.version)
        except Exception as exc:
            print('Registry action not completed; log runs are still valid:',str(exc)[:300])
    print('SUCCESS: Remote logging completed. Open the DagsHub project MLflow UI to verify.')


if __name__=='__main__':
    action=sys.argv[1] if len(sys.argv)>1 else 'local'
    {'local':run_local,'experiments':new_runs,'remote':remote_sync}[action]()
