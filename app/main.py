import os, re
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

NUM_RE = re.compile(r"^-?\d+$")
ALPHA_RE = re.compile(r"^[A-Za-z]+$")

app = FastAPI()

FULL_NAME = os.getenv("APP_FULL_NAME", "John Doe")
DOB_DDMMYYYY = os.getenv("APP_DOB_DDMMYYYY", "17091999")
EMAIL = os.getenv("APP_EMAIL", "john@xyz.com")
ROLL = os.getenv("APP_ROLL_NUMBER", "ABCD123")

def build_user_id(full_name: str, dob: str) -> str:
    base = "_".join([p for p in full_name.lower().strip().split() if p])
    return f"{base}_{dob.strip()}" if dob else base

def alternating_caps_reverse(letters: str) -> str:
    out, idx = [], 0
    for ch in reversed(letters or ""):
        if ch.isalpha():
            out.append(ch.upper() if idx % 2 == 0 else ch.lower())
            idx += 1
    return "".join(out)

@app.get("/")  # quick health check
def root():
    return {"status": "ok"}

@app.post("/bfhl")
async def bfhl(req: Request):
    res = {
        "is_success": False,
        "user_id": build_user_id(FULL_NAME, DOB_DDMMYYYY),
        "email": EMAIL,
        "roll_number": ROLL,
        "odd_numbers": [],
        "even_numbers": [],
        "alphabets": [],
        "special_characters": [],
        "sum": "0",
        "concat_string": ""
    }
    try:
        payload = await req.json()
        data = payload.get("data", [])
        sdata = [str(x) if x is not None else "" for x in data]

        even, odd, alpha_upper, special = [], [], [], []
        total = 0
        letters_stream = []

        for s in sdata:
            if NUM_RE.match(s):
                n = int(s); total += n
                (even if n % 2 == 0 else odd).append(s)
            elif ALPHA_RE.match(s):
                alpha_upper.append(s.upper())
                letters_stream.append(s)
            else:
                special.append(s)

        concat = alternating_caps_reverse("".join(letters_stream))

        res.update({
            "is_success": True,
            "odd_numbers": odd,
            "even_numbers": even,
            "alphabets": alpha_upper,
            "special_characters": special,
            "sum": str(total),
            "concat_string": concat
        })
        return JSONResponse(status_code=200, content=res)
    except Exception:
        return JSONResponse(status_code=200, content=res)
