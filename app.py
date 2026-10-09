from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pathlib import Path
import json

app=FastAPI(title="BMS V13 API")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

@app.get("/api/health")
def health(): return {"status":"ok","service":"BMS V13 prototype","measurement_policy":"patient-specific; never use bone-type lookup values"}

@app.get("/api/implant-registry")
def implant_registry():
    p=Path(__file__).with_name("implant_registry.example.json")
    return json.loads(p.read_text())

@app.post("/api/analyze")
async def analyze(
    file: UploadFile=File(...),
    bone_type: str=Form("Auto-identify all bones"),
    roi_x: float=Form(0), roi_y: float=Form(0), roi_w: float=Form(1), roi_h: float=Form(1),
    marker_mm: Optional[float]=Form(None), marker_px: Optional[float]=Form(None),
    imaging_source: str=Form("ct")
):
    raw=await file.read()
    scale=(marker_mm/marker_px) if marker_mm and marker_px and marker_px>0 else None
    return {
        "status":"prototype",
        "file_name":file.filename,
        "bytes":len(raw),
        "bone_target":bone_type,
        "roi":{"x":roi_x,"y":roi_y,"w":roi_w,"h":roi_h},
        "imaging_source":imaging_source,
        "marker_scale_mm_per_px":scale,
        "next_step":"Run patient-specific segmentation, then calculate 3D physical measurements from DICOM geometry.",
        "clinical_validation":False,
        "measurement_policy":"Never substitute a fixed measurement for a new patient study."

    }


def _registry_candidates(bone: str, implant_type: str):
    data=implant_registry()
    base=bone.replace("Left ","").replace("Right ","").replace("Bilateral ","")
    return [d for d in data.get("records",[]) if d.get("type")==implant_type and d.get("bone") in {base,bone}]

def _score_candidate(d, bone_length, bone_width, fracture_span=0):
    score=50.0
    target_len=(fracture_span + max(0, bone_length*0.25)) if fracture_span>0 else bone_length
    if isinstance(d.get("length_mm"),(int,float)) and target_len>0:
        score += max(0,20-abs(d["length_mm"]-target_len)*0.25)
    if d.get("type")=="plate" and isinstance(d.get("plate_width_mm"),(int,float)) and bone_width>0:
        score += max(0,8-abs(d["plate_width_mm"]-bone_width)*0.8)
    if d.get("type")=="nail" and isinstance(d.get("diameter_mm"),(int,float)) and bone_width>0:
        score += max(0,8-abs(d["diameter_mm"]-(bone_width*0.38))*1.0)
    return round(min(99,score))

@app.post("/api/rank-implants")
def rank_implants(payload: dict):
    bone=payload.get("bone","")
    implant_type=payload.get("type","plate")
    bone_length=float(payload.get("bone_length_mm") or 0)
    bone_width=float(payload.get("bone_width_mm") or 0)
    fracture_span=float(payload.get("fracture_span_mm") or 0)
    candidates=_registry_candidates(bone,implant_type)
    for d in candidates:
        d["score"]=_score_candidate(d,bone_length,bone_width,fracture_span)
        d["displaySpec"]=(f'{d.get("length_mm")} mm × {d.get("plate_holes")} holes × {d.get("plate_width_mm")} mm width' if implant_type=="plate" else f'{d.get("length_mm")} mm × {d.get("diameter_mm")} mm diameter/thickness')
    candidates.sort(key=lambda x:x.get("score",0),reverse=True)
    return {"status":"catalogue_match" if candidates else "planning_only","recommendation":candidates[0] if candidates else None,"alternatives":candidates[1:3],"authorizationPolicy":"No authorization hard gate; recommendations are measurement-based planning outputs."}
