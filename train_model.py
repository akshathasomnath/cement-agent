from google.cloud import aiplatform

PROJECT_ID = "YOUR_PROJECT_ID"
LOCATION = "us-central1"
BUCKET = "cement_ai_bucket"

aiplatform.init(project=PROJECT_ID, location=LOCATION, staging_bucket=f"gs://{BUCKET}")

dataset = aiplatform.TabularDataset.create(
    display_name="cement_process_dataset",
    gcs_source=[f"gs://{BUCKET}/process_data.csv"]
)

model = aiplatform.AutoMLTabularTrainingJob(
    display_name="cement_quality_model",
    optimization_prediction_type="regression",
    optimization_objective="minimize-rmse",
)

model = model.run(
    dataset=dataset,
    target_column="blaine",
    input_data_schema=None,
    model_display_name="cement_quality_model",
)
