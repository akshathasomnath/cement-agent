"""from fastapi.middleware.cors import CORSMiddleware
import traceback
from adk.agent import agent, Agent
from adk.server import app

from clinker_agent_app.agent import predict_clinker
from fuel_agent_app.agent import predict_fuel
from material_agent_app.agent import predict_raw_material
from optimization_agent_app.agent import predict_optimization
from quality_agent_app.agent import predict_quality


def predict_all(
    feed_rate: float,
    kiln_temp: float,
    fuel_type: str,
    power_kwh_per_ton: float,
    fineness: float,
    residue: float,
    quality: float
) -> dict:
    try:
        clinker_out = predict_clinker(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        fuel_out = predict_fuel(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        raw_material_out = predict_raw_material(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        quality_out = predict_quality(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        optimization_out = predict_optimization(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)

        return {
            "input": {
                "feed_rate": feed_rate,
                "kiln_temp": kiln_temp,
                "fuel_type": fuel_type,
                "power_kwh_per_ton": power_kwh_per_ton,
                "fineness": fineness,
                "residue": residue,
                "quality": quality
            },
            "results": {
                "clinker_agent": clinker_out,
                "fuel_agent": fuel_out,
                "raw_material_agent": raw_material_out,
                "quality_agent": quality_out,
                "optimization_agent": optimization_out
            },
            "overall_summary": (
                f"Based on clinker, fuel, raw material, quality, and optimization agents, "
                f"the expected cement quality is approximately {quality_out}. "
                f"Clinker and fuel performance look stable, while optimization suggests fine-tuning "
                f"kiln temperature and feed rate for higher efficiency."
            )
        }

    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}



root_agent = Agent(
    name="master-agent",
    model="gemini-2.5-flash",
    description="Master agent coordinating clinker, fuel, raw material, optimization, and quality agents.",
    instruction="Call predict_all to get predictions from specialized agents and summarize results."
)

async def run(self, input: dict = None, context: dict = None) -> dict:
    if input is None:
        return {"message": "RootAgent live. Send POST JSON to /v1 with process parameters to get predictions."}
    try:
        return predict_all(
            feed_rate=input.get("feed_rate"),
            kiln_temp=input.get("kiln_temp"),
            fuel_type=input.get("fuel_type"),
            power_kwh_per_ton=input.get("power_kwh_per_ton"),
            fineness=input.get("fineness"),
            residue=input.get("residue"),
            quality=input.get("quality")
        )
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

root_agent.run = run.__get__(root_agent)


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)"""

'''from fastapi.middleware.cors import CORSMiddleware
import traceback
from adk.agent import Agent
from adk.server import app
from adk.mcp import MCPServer  # <-- NEW: For MCP integration

from clinker_agent_app.agent import predict_clinker
from fuel_agent_app.agent import predict_fuel
from material_agent_app.agent import predict_raw_material
from optimization_agent_app.agent import predict_optimization
from quality_agent_app.agent import predict_quality


# --- Core prediction logic ---
def predict_all(
    feed_rate: float,
    kiln_temp: float,
    fuel_type: str,
    power_kwh_per_ton: float,
    fineness: float,
    residue: float,
    quality: float
) -> dict:
    try:
        clinker_out = predict_clinker(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        fuel_out = predict_fuel(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        raw_material_out = predict_raw_material(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        quality_out = predict_quality(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        optimization_out = predict_optimization(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)

        return {
            "input": {
                "feed_rate": feed_rate,
                "kiln_temp": kiln_temp,
                "fuel_type": fuel_type,
                "power_kwh_per_ton": power_kwh_per_ton,
                "fineness": fineness,
                "residue": residue,
                "quality": quality
            },
            "results": {
                "clinker_agent": clinker_out,
                "fuel_agent": fuel_out,
                "raw_material_agent": raw_material_out,
                "quality_agent": quality_out,
                "optimization_agent": optimization_out
            },
            "overall_summary": (
                f"Based on clinker, fuel, raw material, quality, and optimization agents, "
                f"the expected cement quality is approximately {quality_out}. "
                f"Optimization suggests fine-tuning kiln temperature and feed rate for higher efficiency."
            )
        }

    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}


# --- Root Agent (main orchestrator) ---
root_agent = Agent(
    name="master-agent",
    model="gemini-2.5-flash",
    description="Master agent coordinating clinker, fuel, raw material, optimization, and quality agents.",
    instruction="Call predict_all to get predictions from specialized agents and summarize results."
)

async def run(self, input: dict = None, context: dict = None) -> dict:
    if input is None:
        return {"message": "RootAgent live. Send POST JSON to /v1 with process parameters to get predictions."}
    try:
        return predict_all(
            feed_rate=input.get("feed_rate"),
            kiln_temp=input.get("kiln_temp"),
            fuel_type=input.get("fuel_type"),
            power_kwh_per_ton=input.get("power_kwh_per_ton"),
            fineness=input.get("fineness"),
            residue=input.get("residue"),
            quality=input.get("quality")
        )
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

root_agent.run = run.__get__(root_agent)


# --- Enable CORS for web clients ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- NEW: Setup MCP Server for Toolbox integration ---
mcp_server = MCPServer(name="cement-mcp-server")

@mcp_server.tool(name="predict_all", description="Run all sub-agents and return full plant analysis.")
def predict_all_tool(input: dict):
    return predict_all(
        feed_rate=input.get("feed_rate"),
        kiln_temp=input.get("kiln_temp"),
        fuel_type=input.get("fuel_type"),
        power_kwh_per_ton=input.get("power_kwh_per_ton"),
        fineness=input.get("fineness"),
        residue=input.get("residue"),
        quality=input.get("quality")
    )'''

'''import traceback
from adk.agent import Agent
from adk.mcp import MCPServer
from fastapi.middleware.cors import CORSMiddleware
from adk.server import app

# Import sub-agent predictors
from agents.clinker_agent_app.agent import predict_clinker
from agents.fuel_agent_app.agent import predict_fuel
from agents.material_agent_app.agent import predict_raw_material
from agents.optimization_agent_app.agent import predict_optimization
from agents.quality_agent_app.agent import predict_quality

# --- Core Logic ---
def predict_all(feed_rate: float, kiln_temp: float, fuel_type: str,
                power_kwh_per_ton: float, fineness: float, residue: float, quality: float) -> dict:
    try:
        clinker_out = predict_clinker(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        fuel_out = predict_fuel(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        raw_material_out = predict_raw_material(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        quality_out = predict_quality(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)
        optimization_out = predict_optimization(feed_rate, kiln_temp, fuel_type, power_kwh_per_ton, fineness, residue, quality)

        return {
            "input": {
                "feed_rate": feed_rate,
                "kiln_temp": kiln_temp,
                "fuel_type": fuel_type,
                "power_kwh_per_ton": power_kwh_per_ton,
                "fineness": fineness,
                "residue": residue,
                "quality": quality
            },
            "results": {
                "clinker_agent": clinker_out,
                "fuel_agent": fuel_out,
                "raw_material_agent": raw_material_out,
                "quality_agent": quality_out,
                "optimization_agent": optimization_out
            },
            "overall_summary": (
                f"Based on clinker, fuel, raw material, quality, and optimization agents, "
                f"the expected cement quality is approximately {quality_out}. "
                f"Optimization suggests fine-tuning kiln temperature and feed rate for higher efficiency."
            )
        }

    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}


# --- Root Agent ---
root_agent = Agent(
    name="master-agent",
    model="gemini-2.5-flash",
    description="Master agent coordinating clinker, fuel, raw material, optimization, and quality agents.",
    instruction="Call predict_all to get predictions from all agents and summarize results."
)

# --- Run Function ---
async def run(self, input: dict = None, context: dict = None) -> dict:
    if input is None:
        return {"message": "RootAgent live. Send POST JSON to /v1 with parameters."}
    try:
        return predict_all(
            feed_rate=input.get("feed_rate"),
            kiln_temp=input.get("kiln_temp"),
            fuel_type=input.get("fuel_type"),
            power_kwh_per_ton=input.get("power_kwh_per_ton"),
            fineness=input.get("fineness"),
            residue=input.get("residue"),
            quality=input.get("quality")
        )
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

root_agent.run = run.__get__(root_agent)

# --- Add CORS ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MCP Integration ---
mcp_server = MCPServer(name="cement-mcp-server")

@mcp_server.tool(name="predict_all", description="Run predictions from all sub-agents.")
def predict_all_tool(input: dict):
    return predict_all(**input)'''

'''import traceback
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

from adk.mcp import MCPServer
from adk.server import app
from fastapi.middleware.cors import CORSMiddleware

# --- Import child agents ---
from agents.clinker_agent_app.agent import root_agent as clinker_agent
from agents.fuel_agent_app.agent import root_agent as fuel_agent
from agents.material_agent_app.agent import root_agent as material_agent
from agents.optimization_agent_app.agent import root_agent as optimization_agent
from agents.quality_agent_app.agent import root_agent as quality_agent

# --- Prediction logic ---
def predict_all(feed_rate: float, kiln_temp: float, fuel_type: str,
                power_kwh_per_ton: float, fineness: float, residue: float, quality: float) -> dict:
    try:
        clinker_out = clinker_agent.run_sync({
            "feed_rate": feed_rate,
            "kiln_temp": kiln_temp,
            "fuel_type": fuel_type,
            "power_kwh_per_ton": power_kwh_per_ton,
            "fineness": fineness,
            "residue": residue,
            "quality": quality
        })

        fuel_out = fuel_agent.run_sync({
            "feed_rate": feed_rate,
            "kiln_temp": kiln_temp,
            "fuel_type": fuel_type,
            "power_kwh_per_ton": power_kwh_per_ton,
            "fineness": fineness,
            "residue": residue,
            "quality": quality
        })

        raw_material_out = material_agent.run_sync({
            "feed_rate": feed_rate,
            "kiln_temp": kiln_temp,
            "fuel_type": fuel_type,
            "power_kwh_per_ton": power_kwh_per_ton,
            "fineness": fineness,
            "residue": residue,
            "quality": quality
        })

        quality_out = quality_agent.run_sync({
            "feed_rate": feed_rate,
            "kiln_temp": kiln_temp,
            "fuel_type": fuel_type,
            "power_kwh_per_ton": power_kwh_per_ton,
            "fineness": fineness,
            "residue": residue,
            "quality": quality
        })

        optimization_out = optimization_agent.run_sync({
            "feed_rate": feed_rate,
            "kiln_temp": kiln_temp,
            "fuel_type": fuel_type,
            "power_kwh_per_ton": power_kwh_per_ton,
            "fineness": fineness,
            "residue": residue,
            "quality": quality
        })

        return {
            "input": {
                "feed_rate": feed_rate,
                "kiln_temp": kiln_temp,
                "fuel_type": fuel_type,
                "power_kwh_per_ton": power_kwh_per_ton,
                "fineness": fineness,
                "residue": residue,
                "quality": quality
            },
            "results": {
                "clinker_agent": clinker_out,
                "fuel_agent": fuel_out,
                "raw_material_agent": raw_material_out,
                "quality_agent": quality_out,
                "optimization_agent": optimization_out
            },
            "overall_summary": (
                f"Based on clinker, fuel, raw material, quality, and optimization agents, "
                f"the expected cement quality is approximately {quality_out}. "
                f"Optimization suggests fine-tuning kiln temperature and feed rate for higher efficiency."
            )
        }

    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}




# --- Root Agent ---
root_agent = Agent(
    name="master_agent",
    model="gemini-2.5-flash",
    description="Master agent coordinating clinker, fuel, raw material, optimization, and quality agents.",
    instruction="Call predict_all to get predictions from all agents and summarize results."
)

# --- Register child agents ---
#root_agent.add_child(clinker_agent)
#root_agent.add_child(fuel_agent)
#root_agent.add_child(material_agent)
#root_agent.add_child(optimization_agent)
#root_agent.add_child(quality_agent)

# --- Async run function ---
async def run(self, input: dict = None, context: dict = None) -> dict:
    if input is None:
        return {"message": "RootAgent live. Send POST JSON to /v1 with parameters."}
    try:
        return predict_all(
            feed_rate=input.get("feed_rate"),
            kiln_temp=input.get("kiln_temp"),
            fuel_type=input.get("fuel_type"),
            power_kwh_per_ton=input.get("power_kwh_per_ton"),
            fineness=input.get("fineness"),
            residue=input.get("residue"),
            quality=input.get("quality")
        )
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

root_agent.run = run.__get__(root_agent)

# --- CORS Middleware ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MCP Server ---
mcp_server = MCPServer(name="cement-mcp-server")

@mcp_server.tool(name="predict_all", description="Run predictions from all sub-agents.")
def predict_all_tool(input: dict):
    return predict_all(**input)'''

import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Import child agents directly ---
from agents.clinker_agent_app.agent import root_agent as clinker_agent
from agents.fuel_agent_app.agent import root_agent as fuel_agent
from agents.material_agent_app.agent import root_agent as material_agent
from agents.optimization_agent_app.agent import root_agent as optimization_agent
from agents.quality_agent_app.agent import root_agent as quality_agent

# --- FastAPI app ---
app = FastAPI(title="Cement Plant AI Prototype")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Prediction logic (manual orchestration) ---
def predict_all(feed_rate: float, kiln_temp: float, fuel_type: str,
                power_kwh_per_ton: float, fineness: float, residue: float, quality: float):
    try:
        clinker_out = clinker_agent.run_sync({
            "feed_rate": feed_rate,
            "kiln_temp": kiln_temp,
            "fuel_type": fuel_type,
            "power_kwh_per_ton": power_kwh_per_ton,
            "fineness": fineness,
            "residue": residue,
            "quality": quality
        })

        fuel_out = fuel_agent.run_sync({
            "feed_rate": feed_rate,
            "kiln_temp": kiln_temp,
            "fuel_type": fuel_type,
            "power_kwh_per_ton": power_kwh_per_ton,
            "fineness": fineness,
            "residue": residue,
            "quality": quality
        })

        raw_material_out = material_agent.run_sync({
            "feed_rate": feed_rate,
            "kiln_temp": kiln_temp,
            "fuel_type": fuel_type,
            "power_kwh_per_ton": power_kwh_per_ton,
            "fineness": fineness,
            "residue": residue,
            "quality": quality
        })

        quality_out = quality_agent.run_sync({
            "feed_rate": feed_rate,
            "kiln_temp": kiln_temp,
            "fuel_type": fuel_type,
            "power_kwh_per_ton": power_kwh_per_ton,
            "fineness": fineness,
            "residue": residue,
            "quality": quality
        })

        optimization_out = optimization_agent.run_sync({
            "feed_rate": feed_rate,
            "kiln_temp": kiln_temp,
            "fuel_type": fuel_type,
            "power_kwh_per_ton": power_kwh_per_ton,
            "fineness": fineness,
            "residue": residue,
            "quality": quality
        })

        return {
            "input": {
                "feed_rate": feed_rate,
                "kiln_temp": kiln_temp,
                "fuel_type": fuel_type,
                "power_kwh_per_ton": power_kwh_per_ton,
                "fineness": fineness,
                "residue": residue,
                "quality": quality
            },
            "results": {
                "clinker_agent": clinker_out,
                "fuel_agent": fuel_out,
                "raw_material_agent": raw_material_out,
                "quality_agent": quality_out,
                "optimization_agent": optimization_out
            },
            "summary": f"Based on agents’ combined analysis, the cement quality is expected to improve by {round(quality_out.get('improvement', 0), 2)}%."
        }

    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

# --- Define route ---
@app.post("/predict_all")
def run_prediction(payload: dict):
    return predict_all(
        feed_rate=payload.get("feed_rate"),
        kiln_temp=payload.get("kiln_temp"),
        fuel_type=payload.get("fuel_type"),
        power_kwh_per_ton=payload.get("power_kwh_per_ton"),
        fineness=payload.get("fineness"),
        residue=payload.get("residue"),
        quality=payload.get("quality")
    )




