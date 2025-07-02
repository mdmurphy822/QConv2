from fastapi import FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse
from parser import parse_quiz_file, extract_text
from validator import validate_output_with_gpt, attempt_fix_with_gpt
import tempfile

app = FastAPI()

@app.post("/upload/auto-correct")
async def upload_and_autocorrect(file: UploadFile = File(...)):
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    raw_text = extract_text(tmp_path, file.filename)
    parsed_output = parse_quiz_file(tmp_path, file.filename)

    validation_result = validate_output_with_gpt(parsed_output)

    if "✅ VALID FILE" in validation_result:
        return PlainTextResponse(parsed_output)
    else:
        corrected_output = attempt_fix_with_gpt(raw_text)
        return PlainTextResponse(corrected_output)
