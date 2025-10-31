import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

class GrindingAgent:
    def __init__(self, project_id, location):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-pro")
        self.chat = self.model.start_chat()
        self.bq_client = bigquery.Client(project=project_id)

    def ask_model(self, prompt: str) -> str:
        response = self.chat.send_message(prompt)
        return response.text

    def get_recent_data(self):
        """Fetch recent grinding logs from BigQuery"""
        query = """
        SELECT * 
        FROM `cement_ai_dataset.grinding_logs`
        ORDER BY timestamp DESC
        LIMIT 100
        """
        try:
            df = self.bq_client.query(query).to_dataframe()
            return df
        except GoogleAPIError as e:
            print(" BigQuery Error:", e)
            return None

    def analyze_and_optimize(self):
        """Fetch logs + ask Gemini for optimization suggestions"""
        df = self.get_recent_data()
        if df is None or df.empty:
            return "No grinding data available in BigQuery."
        
        summary = df.head(10).to_string()  
        prompt = f"""
        You are an AI agent optimizing cement grinding.
        Here are recent logs:
        {summary}

        Please summarize issues and suggest 3 optimization steps.
        """
        return self.ask_model(prompt)
