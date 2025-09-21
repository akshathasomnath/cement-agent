from google.cloud import aiplatform

aiplatform.init(project="glossy-observer-425809-e5", location="us-central1")

model_id = "2298431201330855936" 

endpoint = aiplatform.Model(model_id).deploy(
    deployed_model_display_name="cement_quality_model",
    machine_type="n1-standard-4"
)

print("Model deployed at endpoint:", endpoint.resource_name)
