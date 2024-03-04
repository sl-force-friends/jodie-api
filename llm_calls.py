"""
llm_calls.py
"""
from typing import Any, Generator

import chromadb
import instructor
from groq import Groq
from openai import AzureOpenAI

from config import (
    AZURE_API_KEY,
    AZURE_API_VER,
    AZURE_ENDPOINT,
    GPT3,
    GPT4,
    GROQ_API_KEY,
    MIXTRAL
    )

from response_models import (
    AlternativeTitles,
    NegativeContentCheck,
    PositiveContentCheck
)

from prompts import (
    CLASSIFY_WHETHER_ACCURATE_JOB_TITLE,
    CLASSIFY_WHETHER_JOB_TITLE,
    CLASSIFY_WHETHER_JOB_DESC,
    SCAN_JOB_DESCRIPTION,
    SUGGEST_ALT_JOB_TITLES,
    PROVIDE_JOB_DESIGN_SUGGESTIONS,
    REWRITE_JOB_DESC,
    generate_job_posting_prompt,
    generate_job_design_rag_prompt
)

client = AzureOpenAI(api_key=AZURE_API_KEY,
                     azure_endpoint=AZURE_ENDPOINT,
                     api_version=AZURE_API_VER)

instructor_client = instructor.patch(AzureOpenAI(api_key=AZURE_API_KEY,
                                                 azure_endpoint=AZURE_ENDPOINT,
                                                 api_version=AZURE_API_VER))

groq_client = Groq(api_key=GROQ_API_KEY)

def is_bad_input(job_title: str, job_description: str) -> int:
    """
    Scans input. Returns 1 if the input is valid, 0 if the input is invalid.
    """
    is_real_job_tile = _zero_shot_classifier(CLASSIFY_WHETHER_JOB_TITLE, job_title)
    is_real_job_description = _zero_shot_classifier(CLASSIFY_WHETHER_JOB_DESC, job_description)
    if is_real_job_tile and is_real_job_description:
        return False
    return True

def check_job_title(job_title: str, job_description: str) -> int:
    """
    Checks if the job title matches the job description. 
    If yes, returns `1`. If no, returns `0`.
    """
    prompt = generate_job_posting_prompt(job_title, job_description)
    result = _zero_shot_classifier(CLASSIFY_WHETHER_ACCURATE_JOB_TITLE, prompt)
    return result

def generate_alt_job_title(job_title: str, job_description: str) -> list[str]:
    """
    Generates alternative job titles based on the job description.
    """
    prompt = generate_job_posting_prompt(job_title, job_description)
    output = _chat_completion(model=GPT3,
                              system_message=SUGGEST_ALT_JOB_TITLES,
                              prompt=prompt,
                              api_client=instructor_client,
                              response_model=AlternativeTitles,
                              max_retries=5)
    return output.alternative_titles

def check_jd_positive_content(job_description: str) -> dict[str, bool]:
    """
    Checks if the positive content can be found in the job desc.
    """
    output: PositiveContentCheck = _chat_completion(model=GPT3,
                                                    system_message=SCAN_JOB_DESCRIPTION,
                                                    prompt=job_description,
                                                    api_client=instructor_client,
                                                    response_model=PositiveContentCheck,
                                                    max_retries=5)
    results = {
        "employee_value_proposition": output.employee_value_proposition,
        "job_summary_and_responsibilities": output.job_summary_and_responsibilities,
        "required_technical_competencies": output.required_technical_competencies,
        "required_behavioural_competencies": output.required_behavioural_competencies,
        "preferred_technical_competencies": output.preferred_technical_competencies,
        "preferred_behavioural_competencies": output.preferred_behavioural_competencies,
        "example_activities": output.example_activities,
        "required_certification": output.required_certification
        }
    return results

def check_jd_negative_content(job_description: str) -> dict[str, bool]:
    """
    Checks if the negative content can be found in the job desc.
    """
    output = _chat_completion(model=GPT3,
                              system_message=SCAN_JOB_DESCRIPTION,
                              prompt=job_description,
                              api_client=instructor_client,
                              response_model=NegativeContentCheck,
                              max_retries=5)
    results = {"required_years_of_experience": output.required_years_of_experience,
                "required_formal_education": output.required_formal_education}
    return results

def generate_job_design_suggestions(job_title: str,
                                    job_description: str,
                                    groq:bool) -> Generator[Any, Any, Any]:
    """
    Generates job design suggestions based on the job description.
    """
    doc_extracts = _get_relevant_chunks(job_title, job_description)
    prompt = generate_job_design_rag_prompt(job_title, job_description, doc_extracts)
    if groq:
        results = _stream_chat_completion(model=MIXTRAL,
                                  system_message=PROVIDE_JOB_DESIGN_SUGGESTIONS,
                                  prompt=prompt,
                                  api_client=groq_client,
                                  stream=True)
    else:
        results = _stream_chat_completion(model=GPT4,
                                        system_message=PROVIDE_JOB_DESIGN_SUGGESTIONS,
                                        prompt=prompt,
                                        stream=True)
    for result in results:
        yield result

def generate_ai_jd(job_title: str,
                   job_description: str,
                   groq:bool) -> Generator[Any, Any, Any]:
    """
    Rewrites the job description based on the job title.
    """
    prompt = generate_job_posting_prompt(job_title, job_description)
    if groq:
        results = _stream_chat_completion(model=MIXTRAL,
                                  system_message=REWRITE_JOB_DESC,
                                  prompt=prompt,
                                  api_client=groq_client,
                                  stream=True)

    else: 
        results = _stream_chat_completion(model=GPT4,
                                      system_message=REWRITE_JOB_DESC,
                                      prompt=prompt,
                                      stream=True)
    for result in results:
        yield result

def _zero_shot_classifier(system_message: str,
                          text_to_classify: str,
                          model: str=GPT3):
    """
    Generic zero-shot binary classifier
    """
    response = _chat_completion(model=model,
                                system_message=system_message,
                                 prompt=text_to_classify,
                                 stream=False,
                                 max_tokens=1,
                                 logit_bias={"15": 100,
                                             "16": 100})
    return int(response)

def _chat_completion(model: str, 
                     system_message: str,
                     prompt: str,
                     api_client=client,
                     **kwargs):
    """Helper function to call the OpenAI API for chat completions."""
    completion = api_client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": prompt}],
        temperature=0,
        seed=1,
        **kwargs
    )

    # if **kwargs contains "response_model"
    if "response_model" in kwargs:
        return completion
    return completion.choices[0].message.content

def _stream_chat_completion(model: str, 
                     system_message: str,
                     prompt: str,
                     api_client=client,
                     **kwargs):
    """Helper function to call the OpenAI API for chat completions."""
    stream = api_client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_message},
                  {"role": "user", "content": prompt}],
        temperature=0,
        seed=1,
        **kwargs
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

def _get_relevant_chunks(title: str, description: str) -> list[str]:
    db_client = chromadb.PersistentClient()
    db_collection = db_client.get_collection(name="ICT_SS")
    results = db_collection.query(query_embeddings=_get_embedding(title+description), n_results = 5)
    documents = results['documents'][0]
    return documents

def _get_embedding(text:str) -> list[float]:
    embeddings = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
        encoding_format="float"
    )
    return embeddings.data[0].embedding
