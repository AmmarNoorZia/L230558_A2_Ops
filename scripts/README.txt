MLflow fix for Step 3
1. Extract ZIP.
2. Merge its contents into existing project root L230558_A2_MLOps.
3. Allow Windows to replace scripts/mlflow_step3.py and 11_OPEN_LOCAL_MLFLOW.bat.
4. Double-click 07_MLFLOW_LOCAL.bat again.
5. If successful, next run 08_THREE_NEW_RUNS.bat, then 09_KERAS_TUNER.bat.
This switches the tracking store to SQLite at mlflow.db. No reinstall or retraining of previously saved models is needed.
