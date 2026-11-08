VISIONGUARD STEP 3 — MLFLOW & KERAS TUNER
=======================================
1. Copy these files and the scripts folder into your EXISTING project root. Merge folders; do not delete or replace old scripts.
2. Run 07_MLFLOW_LOCAL.bat. This installs 3 libraries, runs TWO real small Keras toy trainings on sklearn's built-in digits dataset, and logs the historical actual baseline, MobileNet head and fine-tuned results from Step 2 to a local MLflow experiment. Previously trained curves are truthfully tagged "imported_from_step2" and are NOT presented as live autologging.
3. Run 08_THREE_NEW_RUNS.bat. Trains THREE new baseline CNN configurations with distinct learning rates for 2 epochs and tracks epochs LIVE. Six meaningful model configurations are then present in the same MLflow experiment. One new run enables TensorFlow autologging; the others use a manual Keras callback.
4. Run 09_KERAS_TUNER.bat. Uses sklearn built-in digits toy data for mini tuner, then searches 8 REAL VisionGuard configurations (dropout, learning rate, trainable MobileNetV2 layer count), 2 epochs each on the local dataset. Saves results to outputs/tuning_results.csv and MLflow. This may take several minutes on CPU.
5. Optional: run 11_OPEN_LOCAL_MLFLOW.bat, open http://127.0.0.1:5000 and screenshot runs and comparisons.
6. DagsHub: first create repo L230558_A2_Ops under your DagsHub account. Create a PERSONAL ACCESS TOKEN in DagsHub Settings > Tokens. Never send token to ChatGPT or paste it in screenshots. In project root make a file .env with:
   MLFLOW_TRACKING_URI=https://dagshub.com/YOUR_DAGSHUB_USERNAME/L230558_A2_Ops.mlflow
   MLFLOW_TRACKING_USERNAME=YOUR_DAGSHUB_USERNAME
   MLFLOW_TRACKING_PASSWORD=YOUR_SECRET_DAGSHUB_TOKEN
   Then double click 10_DAGSHUB_SYNC.bat. It will upload the real recorded data and register baseline and champion models when supported by the tracking server.
7. Collect screenshots. Store PDF report interpretation alongside these actual results, do not fabricate runs.
8. Future scripts will handle Flask/DB/Docker/API/cloud. In an emergency, prioritize these over extensive report polishing.
Caution: The Step 2 champions are picked by VALIDATION F1; test metrics for the fine-tuned model are not necessarily metrics of the selected head champion. Your champion may be the head model due to a tie.
