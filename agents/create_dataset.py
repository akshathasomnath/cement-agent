from google.cloud import aiplatform

aiplatform.init(project="glossy-observer-425809-e5", location="us-central1")

dataset = aiplatform.TabularDataset.create(
    display_name="cement_dataset",
    gcs_source=["gs://cement-ai-data-2025/cement_quality.csv"]
)

print("Dataset created:", dataset.resource_name)
