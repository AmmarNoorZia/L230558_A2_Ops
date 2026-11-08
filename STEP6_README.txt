VISIONGUARD STEP 6 — CLOUD API AND FLASK INTEGRATION

Cloud provider: Modal. Existing model: models/champion.keras (local source).
Your DagsHub and Docker files remain unchanged.

1. Merge contents of ZIP into main project folder L230558_A2_MLOps.
2. Sign up at https://modal.com (Starter: currently includes free compute credits).
3. Run 21_CLOUD_INSTALL.bat.
4. Run 22_CLOUD_LOGIN.bat and follow browser authorization.
5. Run 23_CLOUD_DEPLOY.bat. The command prints a PUBLIC .modal.run URL.
   Model is sent privately from your laptop during deployment, no re-training.
6. Run 24_CLOUD_CONNECT.bat. Paste the public URL without /predict if possible.
   This writes PREDICTION_API_URL to existing .env WITHOUT changing MLflow credentials.
7. STOP old localhost Flask process with Ctrl+C; run 13_START_FLASK.bat.
8. Visit http://127.0.0.1:5000/health. Expect model_source = cloud-api.
9. Upload an image in the local Flask website; check prediction and History.
10. Run 25_CLOUD_TEST.bat to verify direct cloud /health and /predict API calls.
11. Screenshot Modal URL and logs, direct health result, /predict result, Flask UI and history.
12. Git commands: git add cloud 21_CLOUD_INSTALL.bat 22_CLOUD_LOGIN.bat 23_CLOUD_DEPLOY.bat 24_CLOUD_CONNECT.bat 25_CLOUD_TEST.bat STEP6_README.txt
    git commit -m "Add Modal cloud inference and Flask integration"
    git push

SECURITY: No tokens in screenshots. Never upload .env or .env.compose.
Notes: Modal is usage-metered and can charge for usage beyond plan credits. Watch spend limits.
The cloud endpoint is public; suitable for coursework but production deployments should add API authentication and abuse controls.
Existing Docker port 5001 still uses local champion model by default; Task 8 is demonstrated on Flask port 5000.
The API will use the exact champion model and same resizing, channel order, and threshold as the local predictor.

Troubleshooting: If running 23 reports a billing/signup restriction, report the exact error.
If cloud health fails on first access, inspect Modal application logs and send nonsecret error text.
