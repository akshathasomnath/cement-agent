# orchestrator_server.py
'''from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from root_agent import root_agent, predict_all  # must import here to trigger child registration


# Import your agents safely
try:
    from agent.root_agent import RootAgent
except ModuleNotFoundError:
    RootAgent = None

try:
    from clinker_agent_app import predict_clinker
except ModuleNotFoundError:
    predict_clinker = None

app = FastAPI(title="Master Orchestrator MCP Server")

# Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint for Cloud Run"""
    return {"status": "Master Orchestrator is running"}

@app.post("/v1")
async def run_agents(request: Request):
    """Main endpoint to route requests to the correct agent"""
    body = await request.json()
    input_data = body.get("input", {})

    # Run clinker prediction
    if "clinker" in input_data and predict_clinker:
        clinker_data = input_data["clinker"]
        result = predict_clinker(**clinker_data)
        return {"clinker_result": result}

    # Run root orchestrator if available
    if RootAgent:
        root_agent = RootAgent()
        result = await root_agent.run(input=input_data)
        return {"root_result": result}

    # Fallback if no agents are loaded
    return {"error": "No active agents found. Please check your configuration."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("orchestrator_server:app", host="0.0.0.0", port=port)'''


'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from root_agent import root_agent  # import global root_agent instance

# Initialize FastAPI
app = FastAPI(title="Cement MCP Orchestrator")

# Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health():
    """Health check endpoint for Cloud Run"""
    return {"status": "MCP Orchestrator running"}

@app.post("/v1")
async def run_agents(request: Request):
    """Main endpoint to orchestrate predictions"""
    try:
        body = await request.json()
        input_data = body.get("input", {})

        # Ensure required fields exist
        if not input_data:
            return {"error": "No input data provided."}

        # Run the root agent (which internally calls all sub-agents)
        result = await root_agent.run(input_data)
        return result

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)'''




'''# orchestrator_server.py
import os
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Any
from google.auth.transport.requests import Request as GoogleRequest
import google.auth

app = FastAPI(title="CementGPT Orchestrator")

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Vertex AI Configuration ---
PROJECT_ID = "glossy-observer-425809-e5"
LOCATION = "us-central1"
ENDPOINT_ID = "7614631494278971392"

VERTEX_AI_ENDPOINT = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}:predict"
)

# Map all agents to the same model endpoint
AGENT_ENDPOINTS = {
    "clinker": VERTEX_AI_ENDPOINT,
    "raw_material": VERTEX_AI_ENDPOINT,
    "fuel": VERTEX_AI_ENDPOINT,
    "optimization": VERTEX_AI_ENDPOINT,
    "quality": VERTEX_AI_ENDPOINT,
}

# --- Local agent import fallback (optional, if running offline) ---
LOCAL_AGENTS_AVAILABLE = False
try:
    from app.agents import clinker as local_clinker
    from app.agents import raw_material as local_raw
    from app.agents import fuel as local_fuel
    from app.agents import optimization as local_opt
    from app.agents import quality as local_quality
    LOCAL_AGENTS_AVAILABLE = True
except Exception:
    LOCAL_AGENTS_AVAILABLE = False


def call_local_agent(name: str, payload: dict) -> Dict[str, Any]:
    """Call local agent functions if they exist."""
    if not LOCAL_AGENTS_AVAILABLE:
        raise RuntimeError("Local agents not available")

    try:
        if name == "clinker":
            return local_clinker.predict_clinker(**payload.get("clinker", {}))
        if name == "raw_material":
            return local_raw.predict_raw_material(**payload.get("raw_material", {}))
        if name == "fuel":
            return local_fuel.predict_fuel_efficiency(**payload.get("fuel", {}))
        if name == "optimization":
            return local_opt.optimize_process(
                clinker=payload.get("clinker_result"),
                raw_material=payload.get("raw_material_result"),
                fuel=payload.get("fuel_result"),
            )
        if name == "quality":
            return local_quality.predict_quality(**payload.get("quality", {}))
    except Exception as e:
        return {"agent_name": name, "status": "error", "message": str(e)}

    return {"agent_name": name, "status": "error", "message": "unknown agent"}


# --- Vertex AI Authenticated Remote Call ---
def call_remote_agent(url: str, payload: dict, timeout: int = 120) -> dict:
    """Authenticated call to Vertex AI endpoint."""
    try:
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        credentials.refresh(GoogleRequest())
        headers = {"Authorization": f"Bearer {credentials.token}"}

        # Vertex AI expects { "instances": [ { "agent_input": payload } ] }
        instance = {"agent_input": payload}
        response = requests.post(url, headers=headers, json={"instances": [instance]}, timeout=timeout)
        response.raise_for_status()

        prediction = response.json()
        return {
            "status": "success",
            "prediction": prediction,
            "agent_output": prediction.get("predictions", [{}])[0] if "predictions" in prediction else {},
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- API Endpoints ---
@app.post("/analyze")
async def analyze(request: Request):
    """Handle single-agent analysis request."""
    body = await request.json()
    agent = body.get("agent")
    payload = body.get("input", {})

    if not agent:
        raise HTTPException(status_code=400, detail="Missing 'agent' in request body")

    if LOCAL_AGENTS_AVAILABLE:
        try:
            result = call_local_agent(agent, {agent: payload})
            return {"status": "success", "agent": agent, "result": result}
        except Exception:
            pass

    url = AGENT_ENDPOINTS.get(agent)
    if not url:
        raise HTTPException(status_code=404, detail=f"No endpoint configured for agent '{agent}'")

    result = call_remote_agent(url, payload)
    return {"status": "success", "agent": agent, "result": result}


@app.post("/run_full_cycle")
async def run_full_cycle(request: Request):
    """Run all agents sequentially and compute efficiency scores."""
    payload = await request.json()
    input_payload = payload or {}

    agent_outputs = {}

    if LOCAL_AGENTS_AVAILABLE:
        try:
            clinker_out = local_clinker.predict_clinker(**input_payload.get("clinker", {}))
            raw_out = local_raw.predict_raw_material(**input_payload.get("raw_material", {}))
            fuel_out = local_fuel.predict_fuel_efficiency(**input_payload.get("fuel", {}))
            optimization_out = local_opt.optimize_process(
                clinker=clinker_out, raw_material=raw_out, fuel=fuel_out
            )
            quality_out = local_quality.predict_quality(**input_payload.get("quality", {}))

            agent_outputs = {
                "clinker": clinker_out,
                "raw_material": raw_out,
                "fuel": fuel_out,
                "optimization": optimization_out,
                "quality": quality_out,
            }
        except Exception:
            agent_outputs = {}

    if not agent_outputs:
        for name, url in AGENT_ENDPOINTS.items():
            agent_outputs[name] = call_remote_agent(url, input_payload)

    # --- Metrics ---
    def compute_pei(agent_outputs: dict):
        values = []
        for out in agent_outputs.values():
            if isinstance(out, dict) and out.get("predicted_efficiency") is not None:
                try:
                    values.append(float(out.get("predicted_efficiency", 0)))
                except Exception:
                    pass
        return round(sum(values) / len(values), 2) if values else 0.0

    def compute_autonomy_score(agent_outputs: dict):
        active = sum(1 for o in agent_outputs.values() if isinstance(o, dict) and o.get("status") == "success")
        total = len(agent_outputs)
        return round((active / total) * 100.0, 2) if total else 0.0

    pei = compute_pei(agent_outputs)
    autonomy_score = compute_autonomy_score(agent_outputs)
    timestamp = datetime.utcnow().isoformat() + "Z"

    return {
        "timestamp": timestamp,
        "agent_outputs": agent_outputs,
        "plant_efficiency_index": pei,
        "autonomy_score": autonomy_score,
    }'''

'''from fastapi import FastAPI
from pydantic import BaseModel
from vertexai.preview.generative_models import GenerativeModel

app = FastAPI(title="Cement Plant GPT Orchestrator")

class PlantQuery(BaseModel):
    query: str

model = GenerativeModel("gemini-1.5-pro")

@app.post("/run_full_cycle")
def run_full_cycle(data: PlantQuery):
    """
    Full autonomous reasoning pipeline:
    1. Energy efficiency analysis
    2. Production optimization
    3. Emission reduction
    4. Explainable recommendation synthesis
    """
    base_prompt = f"""
You are Cement Plant GPT, an expert digital twin of a cement plant.
Given the query: "{data.query}", perform these tasks step-by-step:

1. **Energy Efficiency Agent** – analyse kiln, mill and motor operations; suggest power-saving steps.
2. **Production Agent** – evaluate throughput, bottlenecks, and quality KPIs.
3. **Emission Agent** – check CO₂, NOx, SOx trends; propose greener alternatives.
4. **Optimization Agent** – integrate all insights to form a concise action plan.
5. **Explainability Layer** – explain *why* each recommendation improves KPIs.

Return a markdown summary with headings and bullet points.
"""
    response = model.generate_content(base_prompt)
    return {"result": response.candidates[0].content.parts[0].text}'''

'''# orchestrator_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import importlib
import sys
import os
import json
import traceback

# ✅ Ensure local imports work inside container
sys.path.append(os.path.dirname(__file__))

app = FastAPI(title="CementGPT Orchestrator")

class RequestData(BaseModel):
    user_input: str

def try_import_agent(agent_name):
    """Tries to import a local agent module, returns module or None."""
    try:
        module = importlib.import_module(f"agents.{agent_name}")
        print(f"✅ Loaded local agent: {agent_name}")
        return module
    except ModuleNotFoundError:
        print(f"⚠️ Local agent not found: {agent_name}")
        return None

# Try loading local agents
AGENT_NAMES = ["clinker", "process", "prediction", "recommendation"]
LOCAL_AGENTS = {}

for name in AGENT_NAMES:
    mod = try_import_agent(name)
    if mod:
        LOCAL_AGENTS[name] = mod

@app.get("/healthz")
def health_check():
    return {"status": "ok", "agents_loaded": list(LOCAL_AGENTS.keys())}

@app.post("/run_full_cycle")
def run_full_cycle(data: RequestData):
    user_input = data.user_input
    print(f"🚀 Running full cycle for input: {user_input}")

    results = {}
    try:
        # Step 1: Clinker optimization
        if "clinker" in LOCAL_AGENTS:
            clinker_result = LOCAL_AGENTS["clinker"].run(user_input)
            results["clinker"] = clinker_result
        else:
            results["clinker"] = {"error": "Clinker agent missing"}

        # Step 2: Process optimization
        if "process" in LOCAL_AGENTS:
            process_result = LOCAL_AGENTS["process"].run(results)
            results["process"] = process_result
        else:
            results["process"] = {"error": "Process agent missing"}

        # Step 3: Prediction
        if "prediction" in LOCAL_AGENTS:
            prediction_result = LOCAL_AGENTS["prediction"].run(results)
            results["prediction"] = prediction_result
        else:
            results["prediction"] = {"error": "Prediction agent missing"}

        # Step 4: Recommendation
        if "recommendation" in LOCAL_AGENTS:
            recommendation_result = LOCAL_AGENTS["recommendation"].run(results)
            results["recommendation"] = recommendation_result
        else:
            results["recommendation"] = {"error": "Recommendation agent missing"}

        return {"status": "success", "results": results}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))'''

'''# orchestrator_server.py
from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import importlib
import sys
import os
import traceback

# Make local imports resilient
sys.path.append(os.path.dirname(__file__))      # allow import when running from repo root
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))  # allow importing app.* modules

app = FastAPI(title="CementGPT Orchestrator")

# Agent module names we expect (prefer these names under app/agents/)
EXPECTED_AGENTS = {
    "clinker": ["clinker"],
    "raw_material": ["raw_material", "raw"],
    "fuel": ["fuel"],
    "optimization": ["optimization", "opt"],
    "quality": ["quality"],
}

def find_agent_module(name_candidates):
    """Try to import module from either app.agents.<name> or agents.<name>."""
    for n in name_candidates:
        for prefix in ("app.agents", "agents", ""):
            try:
                mod_name = f"{prefix}.{n}" if prefix else n
                module = importlib.import_module(mod_name)
                print(f"✅ Loaded agent module: {mod_name}")
                return module
            except ModuleNotFoundError:
                continue
            except Exception as e:
                print(f"⚠️ Error importing {n} from {prefix}: {e}")
                continue
    return None

# load available agents (best-effort)
AGENTS = {}
for logical_name, cand in EXPECTED_AGENTS.items():
    mod = find_agent_module(cand)
    if mod:
        AGENTS[logical_name] = mod

@app.get("/healthz")
def healthz():
    return {"status": "ok", "agents_loaded": list(AGENTS.keys())}

def safe_get_first_float(obj, keys, default=0.0):
    """Utility to extract first numeric value from dict using candidate keys or nested list."""
    if not isinstance(obj, dict):
        return default
    for k in keys:
        v = obj.get(k)
        if v is None:
            continue
        # if it's a list with numeric first element
        if isinstance(v, (list, tuple)) and len(v) > 0:
            try:
                return float(v[0])
            except Exception:
                continue
        # numeric-like
        try:
            return float(v)
        except Exception:
            continue
    return default

def compute_pei(agent_outputs: dict):
    """Compute PEI using the same heuristic as dashboard."""
    clinker_val = safe_get_first_float(agent_outputs.get("clinker", {}), ["clinker_prediction", "clinker_efficiency", "predicted_efficiency"])
    raw_val = safe_get_first_float(agent_outputs.get("raw_material", {}), ["raw_material_score", "raw_score", "predicted_efficiency"])
    fuel_val = safe_get_first_float(agent_outputs.get("fuel", {}), ["fuel_efficiency", "efficiency", "predicted_efficiency"])
    opt_val = safe_get_first_float(agent_outputs.get("optimization", {}), ["process_index", "process_score", "predicted_efficiency"])
    qual_val = safe_get_first_float(agent_outputs.get("quality", {}), ["quality_score", "quality", "predicted_efficiency"])

    # weights: clinker 0.3, raw 0.2, fuel 0.2, opt 0.2, qual 0.1
    pei = 0.3 * clinker_val + 0.2 * raw_val + 0.2 * fuel_val + 0.2 * opt_val + 0.1 * qual_val
    try:
        pei = round(float(pei), 2)
    except Exception:
        pei = 0.0
    return max(0.0, min(100.0, pei))

def compute_autonomy_score(agent_outputs: dict):
    """Simple autonomy score: percent of agents that returned valid dict (no 'error')."""
    total = 0
    active = 0
    for k in EXPECTED_AGENTS.keys():
        total += 1
        out = agent_outputs.get(k)
        if isinstance(out, dict) and out.get("error") is None:
            active += 1
    if total == 0:
        return 0.0
    return round((active / total) * 100.0, 2)

@app.post("/run_full_cycle")
async def run_full_cycle(request: Request):
    """
    Accepts a JSON payload like:
    {
      "clinker": {...},
      "raw_material": {...},
      "fuel": {...},
      "quality": {...}
    }
    Calls local agents (if available) and returns combined summary.
    """
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    # Prepare output container
    agent_outputs = {}

    try:
        # 1) Clinker
        if "clinker" in AGENTS:
            try:
                fn = getattr(AGENTS["clinker"], "predict_clinker", None) or getattr(AGENTS["clinker"], "run", None)
                if fn:
                    clinker_in = payload.get("clinker", {})
                    agent_outputs["clinker"] = fn(**clinker_in) if callable(fn) else {"error": "clinker fn not callable"}
                else:
                    agent_outputs["clinker"] = {"error": "clinker function missing"}
            except Exception as e:
                agent_outputs["clinker"] = {"error": str(e)}
        else:
            agent_outputs["clinker"] = {"error": "Clinker agent not available"}

        # 2) Raw material
        if "raw_material" in AGENTS:
            try:
                fn = getattr(AGENTS["raw_material"], "predict_raw_material", None) or getattr(AGENTS["raw_material"], "run", None)
                raw_in = payload.get("raw_material", {})
                agent_outputs["raw_material"] = fn(**raw_in) if callable(fn) else {"error": "raw_material fn not callable"}
            except Exception as e:
                agent_outputs["raw_material"] = {"error": str(e)}
        else:
            agent_outputs["raw_material"] = {"error": "Raw material agent not available"}

        # 3) Fuel
        if "fuel" in AGENTS:
            try:
                fn = getattr(AGENTS["fuel"], "predict_fuel_efficiency", None) or getattr(AGENTS["fuel"], "run", None)
                fuel_in = payload.get("fuel", {})
                agent_outputs["fuel"] = fn(**fuel_in) if callable(fn) else {"error": "fuel fn not callable"}
            except Exception as e:
                agent_outputs["fuel"] = {"error": str(e)}
        else:
            agent_outputs["fuel"] = {"error": "Fuel agent not available"}

        # 4) Optimization (requires earlier outputs)
        if "optimization" in AGENTS:
            try:
                fn = getattr(AGENTS["optimization"], "optimize_process", None) or getattr(AGENTS["optimization"], "run", None)
                if callable(fn):
                    # pass precomputed partial results
                    agent_outputs["optimization"] = fn(
                        clinker=agent_outputs.get("clinker", {}),
                        raw_material=agent_outputs.get("raw_material", {}),
                        fuel=agent_outputs.get("fuel", {})
                    )
                else:
                    agent_outputs["optimization"] = {"error": "optimization fn missing"}
            except Exception as e:
                agent_outputs["optimization"] = {"error": str(e)}
        else:
            agent_outputs["optimization"] = {"error": "Optimization agent not available"}

        # 5) Quality
        if "quality" in AGENTS:
            try:
                fn = getattr(AGENTS["quality"], "predict_quality", None) or getattr(AGENTS["quality"], "run", None)
                quality_in = payload.get("quality", {})
                agent_outputs["quality"] = fn(**quality_in) if callable(fn) else {"error": "quality fn not callable"}
            except Exception as e:
                agent_outputs["quality"] = {"error": str(e)}
        else:
            agent_outputs["quality"] = {"error": "Quality agent not available"}

        # Compute PEI and autonomy
        pei = compute_pei(agent_outputs)
        autonomy_score = compute_autonomy_score(agent_outputs)
        timestamp = datetime.utcnow().isoformat() + "Z"

        response = {
            "status": "success",
            "agent_outputs": agent_outputs,
            "plant_efficiency_index": pei,
            "autonomy_score": autonomy_score,
            "timestamp": timestamp
        }
        return response

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))'''
    
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import importlib
import sys
import os
import traceback

# Make local imports resilient
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

app = FastAPI(title="CementGPT Orchestrator")

# Allow cross-origin requests (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print("🚀 CementGPT Orchestrator starting up")

EXPECTED_AGENTS = {
    "clinker": ["clinker"],
    "raw_material": ["raw_material", "raw"],
    "fuel": ["fuel"],
    "optimization": ["optimization", "opt"],
    "quality": ["quality"],
}

def find_agent_module(name_candidates):
    for n in name_candidates:
        for prefix in ("app.agents", "agents", ""):
            try:
                mod_name = f"{prefix}.{n}" if prefix else n
                module = importlib.import_module(mod_name)
                print(f"✅ Loaded agent module: {mod_name}")
                return module
            except ModuleNotFoundError:
                continue
            except Exception as e:
                print(f"⚠️ Error importing {n} from {prefix}: {e}")
                continue
    return None

# load available agents (best-effort)
AGENTS = {}
for logical_name, cand in EXPECTED_AGENTS.items():
    mod = find_agent_module(cand)
    if mod:
        AGENTS[logical_name] = mod

@app.get("/healthz")
def healthz():
    return {"status": "ok", "agents_loaded": list(AGENTS.keys())}

def safe_get_first_float(obj, keys, default=0.0):
    if not isinstance(obj, dict):
        return default
    for k in keys:
        v = obj.get(k)
        if v is None:
            continue
        if isinstance(v, (list, tuple)) and len(v) > 0:
            try:
                return float(v[0])
            except Exception:
                continue
        try:
            return float(v)
        except Exception:
            continue
    return default

def compute_pei(agent_outputs: dict):
    clinker_val = safe_get_first_float(agent_outputs.get("clinker", {}), ["clinker_prediction", "clinker_efficiency", "predicted_efficiency"])
    raw_val = safe_get_first_float(agent_outputs.get("raw_material", {}), ["raw_material_score", "raw_score", "predicted_efficiency"])
    fuel_val = safe_get_first_float(agent_outputs.get("fuel", {}), ["fuel_efficiency", "efficiency", "predicted_efficiency"])
    opt_val = safe_get_first_float(agent_outputs.get("optimization", {}), ["process_index", "process_score", "predicted_efficiency"])
    qual_val = safe_get_first_float(agent_outputs.get("quality", {}), ["quality_score", "quality", "predicted_efficiency"])

    pei = 0.3 * clinker_val + 0.2 * raw_val + 0.2 * fuel_val + 0.2 * opt_val + 0.1 * qual_val
    try:
        pei = round(float(pei), 2)
    except Exception:
        pei = 0.0
    return max(0.0, min(100.0, pei))

def compute_autonomy_score(agent_outputs: dict):
    total = 0
    active = 0
    for k in EXPECTED_AGENTS.keys():
        total += 1
        out = agent_outputs.get(k)
        if isinstance(out, dict) and out.get("error") is None:
            active += 1
    if total == 0:
        return 0.0
    return round((active / total) * 100.0, 2)

@app.post("/run_full_cycle")
async def run_full_cycle(request: Request):
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    agent_outputs = {}
    try:
        # Clinker
        if "clinker" in AGENTS:
            try:
                fn = getattr(AGENTS["clinker"], "predict_clinker", None) or getattr(AGENTS["clinker"], "run", None)
                if fn:
                    clinker_in = payload.get("clinker", {})
                    agent_outputs["clinker"] = fn(**clinker_in) if callable(fn) else {"error": "clinker fn not callable"}
                else:
                    agent_outputs["clinker"] = {"error": "clinker function missing"}
            except Exception as e:
                agent_outputs["clinker"] = {"error": str(e)}
        else:
            agent_outputs["clinker"] = {"error": "Clinker agent not available"}

        # Raw material
        if "raw_material" in AGENTS:
            try:
                fn = getattr(AGENTS["raw_material"], "predict_raw_material", None) or getattr(AGENTS["raw_material"], "run", None)
                raw_in = payload.get("raw_material", {})
                agent_outputs["raw_material"] = fn(**raw_in) if callable(fn) else {"error": "raw_material fn not callable"}
            except Exception as e:
                agent_outputs["raw_material"] = {"error": str(e)}
        else:
            agent_outputs["raw_material"] = {"error": "Raw material agent not available"}

        # Fuel
        if "fuel" in AGENTS:
            try:
                fn = getattr(AGENTS["fuel"], "predict_fuel_efficiency", None) or getattr(AGENTS["fuel"], "run", None)
                fuel_in = payload.get("fuel", {})
                agent_outputs["fuel"] = fn(**fuel_in) if callable(fn) else {"error": "fuel fn not callable"}
            except Exception as e:
                agent_outputs["fuel"] = {"error": str(e)}
        else:
            agent_outputs["fuel"] = {"error": "Fuel agent not available"}

        # Optimization
        if "optimization" in AGENTS:
            try:
                fn = getattr(AGENTS["optimization"], "optimize_process", None) or getattr(AGENTS["optimization"], "run", None)
                if callable(fn):
                    agent_outputs["optimization"] = fn(
                        clinker=agent_outputs.get("clinker", {}),
                        raw_material=agent_outputs.get("raw_material", {}),
                        fuel=agent_outputs.get("fuel", {})
                    )
                else:
                    agent_outputs["optimization"] = {"error": "optimization fn missing"}
            except Exception as e:
                agent_outputs["optimization"] = {"error": str(e)}
        else:
            agent_outputs["optimization"] = {"error": "Optimization agent not available"}

        # Quality
        if "quality" in AGENTS:
            try:
                fn = getattr(AGENTS["quality"], "predict_quality", None) or getattr(AGENTS["quality"], "run", None)
                quality_in = payload.get("quality", {})
                agent_outputs["quality"] = fn(**quality_in) if callable(fn) else {"error": "quality fn not callable"}
            except Exception as e:
                agent_outputs["quality"] = {"error": str(e)}
        else:
            agent_outputs["quality"] = {"error": "Quality agent not available"}

        pei = compute_pei(agent_outputs)
        autonomy_score = compute_autonomy_score(agent_outputs)
        timestamp = datetime.utcnow().isoformat() + "Z"

        response = {
            "status": "success",
            "agent_outputs": agent_outputs,
            "plant_efficiency_index": pei,
            "autonomy_score": autonomy_score,
            "timestamp": timestamp
        }
        return response

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


