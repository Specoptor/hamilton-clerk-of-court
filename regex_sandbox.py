import json
from utils import extract_datapoints_from_pdf
# from PDF_extractor import extract_property_address
with open('parsed_pdfs.json', 'r') as f:
    parsed_pdfs = json.load(f)

datapoints_dict = {}
for case_number, pdf in parsed_pdfs.items():
    if case_number == "A2303511":
        datapoints_dict[case_number] = extract_datapoints_from_pdf(pdf)

with open('datapoints_sandbox.json', 'w') as f:
    json.dump(datapoints_dict, f)
