from utils import get_processed_pdfs, extract_datapoints_from_pdf
import json

if __name__ == '__main__':
    list_of_pdfs = get_processed_pdfs()  # this will take a while, since it runs on the entire directory
    datapoints_list = {}
    for case_number, pdf_pages_list in list_of_pdfs.items():
        datapoints_list[case_number] = extract_datapoints_from_pdf(pdf_pages_list)

    with open('datapoints_list.json', 'w') as f:
        json.dump(datapoints_list, f, indent=4)
