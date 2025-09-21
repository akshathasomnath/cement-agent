from fastapi.middleware.cors import CORSMiddleware
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
)
