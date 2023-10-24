from utils import get_processed_pdfs, extract_datapoints_from_pdf

if __name__ == '__main__':
    list_of_pdfs = get_processed_pdfs()  # this will take a while, since it runs on the entire directory
    datapoints_list = {}
    for case_number, pdf_pages_list in list_of_pdfs.items():
        datapoints_list[case_number] = extract_datapoints_from_pdf(pdf_pages_list)
    print(datapoints_list)
