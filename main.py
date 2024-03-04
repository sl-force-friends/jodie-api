"""
main.py
"""
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse

from llm_calls import (
    is_bad_input,
    check_job_title,
    check_jd_positive_content,
    check_jd_negative_content,
    generate_alt_job_title,
    generate_job_design_suggestions,
    generate_ai_jd
)

from config import (
    API_KEY,
    JDRequest
    )

# Initialise client
app = FastAPI()

async def get_api_key(x_api_key: str = Header(...)):
    """
    Authenticate the API Key
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=400, detail="Invalid API Key")

# GET endpoint to serve as a GET ping
@app.get("/")
@app.get("/healthcheck")
async def ping():
    """
    GET endpoint to check if the server is running.
    """
    return {"status": "ok"}

# POST endpoint to check job title
@app.post("/title_check")
async def title_check(request: JDRequest,
                      api_key: str = Depends(get_api_key)):
    """
    POST endpoint to check if the job title is a good fit for the job description
    """
    job_title, job_description = _extract_output(request)
    if is_bad_input(job_title, job_description):
        return "Please enter a valid job title/description."
    return check_job_title(job_title, job_description)

# POST endpoint to check job title
@app.post("/alt_titles")
async def alt_titles(request: JDRequest,
                     api_key: str = Depends(get_api_key)):
    """
    POST endpoint to generate alternative job titles
    """
    job_title, job_description = _extract_output(request)
    if is_bad_input(job_title, job_description):
        return "Please enter a valid job title/description."
    return generate_alt_job_title(job_title, job_description)

# POST endpoint to check job description
@app.post("/positive_content_check")
async def positive_content_check(request: JDRequest,
                                 api_key: str = Depends(get_api_key)):
    """
    POST endpoint to check if positive content is present in the job description
    """
    job_title, job_description = _extract_output(request)
    if is_bad_input(job_title, job_description):
        return "Please enter a valid job title/description."
    return check_jd_positive_content(job_description)

# POST endpoint to check job description
@app.post("/negative_content_check")
async def negative_content_check(request: JDRequest,
                                 api_key: str = Depends(get_api_key)):
    """
    POST endpoint to check if negative content is present in the job description
    """
    job_title, job_description = _extract_output(request)
    if is_bad_input(job_title, job_description):
        return "Please enter a valid job title/description."
    return check_jd_negative_content(job_description)

# POST endpoint to check job description
@app.post("/job_design_suggestions")
async def job_design_suggestions(request: JDRequest,
                                 api_key: str = Depends(get_api_key)):
    """
    POST streaming endpoint to generate job design suggestions
    """
    job_title, job_description = _extract_output(request)
    if is_bad_input(job_title, job_description):
        return "Please enter a valid job title/description."
    return StreamingResponse(generate_job_design_suggestions(job_title, job_description),
                             media_type="text/event-stream")

# POST endpoint to check job description
@app.post("/rewrite_jd")
async def rewrite_jd(request: JDRequest,
                     api_key: str = Depends(get_api_key)):
    """
    POST streaming endpoint to re-re-write the job description
    """
    job_title, job_description = _extract_output(request)
    if is_bad_input(job_title, job_description):
        return "Please enter a valid job title/description."
    job_title, job_description = _extract_output(request)
    return StreamingResponse(generate_ai_jd(job_title, job_description), 
                             media_type="text/event-stream") 

def _extract_output(request: JDRequest) -> tuple[str, str]:
    return request.job_title, request.job_description
