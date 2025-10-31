from google.cloud import aiplatform

def main():
    PROJECT_ID ="glassy-observer-425809-e5"          
    LOCATION = "us-central1"
    DATASET_ID = "2102083163621687296"  
    TARGET_COLUMN = "power_kwh_per_ton"
from google.cloud import aiplatform


PROJECT_ID = "glossy-observer-425809-e5"
LOCATION = "us-central1"
DATASET_RESOURCE = "projects/112091879413/locations/us-central1/datasets/4616780605554688000"
TARGET_COLUMN = "power_kwh_per_ton"

MODEL_DISPLAY_NAME = "cement_quality_model"
BUDGET_MILLI_NODE_HOURS = 1000



aiplatform.init(project=PROJECT_ID, location=LOCATION)


dataset = aiplatform.TabularDataset(DATASET_RESOURCE)
print("Dataset loaded. Columns:", dataset.column_names)


job = aiplatform.AutoMLTabularTrainingJob(
    display_name="cement_quality_training_job",
    optimization_prediction_type="regression", 
    optimization_objective="minimize-rmse"
)

print(" Starting training job (this may take many minutes)...")
model = job.run(
    dataset=dataset,
    target_column=TARGET_COLUMN,
    model_display_name=MODEL_DISPLAY_NAME,
    training_fraction_split=0.7,
    validation_fraction_split=0.2,
    test_fraction_split=0.1,
    budget_milli_node_hours=BUDGET_MILLI_NODE_HOURS,
    disable_early_stopping=False,
)

print(" Training complete. Model resource name:", model.resource_name)


