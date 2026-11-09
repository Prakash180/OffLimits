from fastapi import FastAPI, Header, HTTPException

from tests.validate import validate_token

app = FastAPI()

@app.get("/validate")
def validate(authorization: str = Header(None)):

    if not authorization:
        raise HTTPException(401, "No Authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        claims = validate_token(token)
        return {
            "valid": True,
            "claims": claims
        }

    except Exception as ex:
        raise HTTPException(
            status_code=401,
            detail=str(ex)
        )