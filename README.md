# BMS V16 Desktop Software

BMS – Bone & Implant Measurement System is packaged as a desktop application shell around the V16 web interface.

## What changed
- Desktop application window instead of requiring a normal browser tab.
- Starts the local FastAPI service automatically on `127.0.0.1:8765`.
- Keeps V9 principal-axis/PCA bone-length calculation in the V16 frontend.
- Keeps digital fluoroscopy + radiopaque marker calibration.
- Keeps patient-specific implant planning without an authorization hard gate.
- Local processing architecture: uploaded study data is intended to remain on the workstation unless future integrations explicitly add remote services.

## Build on Windows
1. Install Python 3.11+.
2. From `app/`, run:
   `python -m pip install -r requirements.txt`
3. Install Node.js 20+.
4. From this project directory:
   `npm install`
5. Build installer + portable executable:
   `npm run dist:win`

The generated Windows installer and portable executable will be placed in `dist/`.

## Clinical status
This package is a software prototype. It is not clinically validated or cleared/approved for autonomous clinical decision-making. Measurements and implant planning require qualified clinician review.
