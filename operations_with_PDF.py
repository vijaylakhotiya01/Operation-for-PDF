import traceback
from os import path

import pdfkit
from fpdf import FPDF
import os, fitz
from PyPDF2 import PdfFileReader, PdfFileWriter
from datetime import datetime,date
import uuid
import subprocess

# import logging
# log = logging.getLogger("django")
# log_info = logging.getLogger("django_info")
# log_debug = logging.getLogger("django_debug")


def merge_pdfs(file_dir=None, input_file_list=[], output_filename=None):
    """
    :function merge_pdfs: Merges N number of pdf files and returns single file.
    :param file_dir: path of input file, also the output file would be placed here.
    :param input_file_list: List of names of file separated by comas(,).
    :param output_filename: Name for output file
    :return: Status of Operation, Name of output file
    """
    # log_info.info(f"merging pdf start {input_file_list if input_file_list else []}")
    if not output_filename:
        output_filename = str(uuid.uuid1()) + '.pdf'

    for file in input_file_list:
        extra_page_path = file
        output_file_path = file_dir + output_filename
        # print(output_file_path, '\n', file_dir + extra_page_path)
        try:
            original_pdf = fitz.open(output_file_path)
            extra_page = fitz.open(file_dir + extra_page_path)
            original_pdf.insertPDF(extra_page)
            original_pdf.saveIncr()  # , incremental=1, encryption=fitz.PDF_ENCRYPT_KEEP)
        except RuntimeError as e:
            extra_page = fitz.open(file_dir + extra_page_path)
            extra_page.save(output_file_path)
            # log_info.info("merging pdf end")
            pass
    return True, output_filename


def convert_html_to_pdf(file_dir='/', html_file='', raw_filename='my_converted_file'):
    """
    :function convert_html_to_pdf: Converts HTML file to pdf file.
    :param file_dir: path of input HTML file, also the output file would be placed here.
    :param html_file: Name of input HTML file
    :param raw_filename: Name of output file // Without extension
    :return: Status of Operation, Name of output file
    """
    if path.isfile(file_dir+'/'+html_file):
        print(file_dir)
        pdf_filename = raw_filename + '.pdf'
        options = {
            'encoding': 'UTF-8',
            'margin-left': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-top': '20mm'
        }

        pdf_status = pdfkit.from_file(file_dir+"/" + str(html_file), file_dir+"/" + pdf_filename, options=options)
        return pdf_status, pdf_filename


def convert_html_content_to_xfile(file_dir='/', required_type='pdf', html_data='', raw_filename='my_converted_file'):
    """
    :function convert_html_content_to_xfile: Converts HTML file to pdf file.
    :param file_dir: path of input HTML file, also the output file would be placed here.
    :param required_type: required type of output file (.html / .pdf).
    :param html_data: String encoded HTML content.
    :param raw_filename: Name of output file // Without extension
    :return: Status of Operation, Name of output file
    """
    if html_data != '':
        html_filename = raw_filename + '.html'
        f = open(file_dir + '/' + html_filename, 'w')
        f.write(html_data)
        f.close()
        if required_type.lower()=='html':
            return True, html_filename
        print(file_dir)
        pdf_status, pdf_filename = convert_html_to_pdf(file_dir=file_dir, html_file=html_filename, raw_filename=raw_filename)
        return pdf_status, pdf_filename


def convert_img_to_pdf(file_dir='', img_file='', raw_filename='my_converted_file'):
    """
    :function convert_img_to_pdf: Converts Image file(.jpg / .png) to pdf file.
    :param file_dir: path of input file, also the output file would be placed here.
    :param img_file: filename of image.
    :param raw_filename: Name of output file // Without extension
    :return: Status of Operation, Name of output file
    """
    with fitz.open(file_dir + img_file) as img, fitz.open() as gen_pdf:
        rect = img[0].rect  # pic dimension
        pdfbytes = img.convertToPDF()  # make a PDF stream
        imgPDF = fitz.open("pdf", pdfbytes)  # open stream as PDF
        page = gen_pdf.newPage(width=rect.width, height=rect.height)  # new page with pic dimension
        page.showPDFpage(rect, imgPDF, 0)
        new_filename = raw_filename + ".pdf"
        gen_pdf.save(new_filename)
    return True, new_filename


def convert_text_to_pdf(new_filename, val):
    """
    :function convert_text_to_pdf: Converts string encoded Text to pdf file.
    :param new_filename: Name of output file.
    :param val: text which needs to be converted in PDF.
    :return: Status of Operation, Name of output file
    """
    text_file_name = new_filename
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=15)  # Specify Font Family and Size here.
    for t in val.split('\n'):   # if text needs to printed at different lines.
        pdf.cell(200, 10, txt=t, ln=1, align='C')   # Starting pixel of Text in PDF page in X-Y axis.
    pdf.output(text_file_name)  # You can add file_dir here, if needs to paste at another location.
    return True, text_file_name


def insert_file_in_pdf(file_dir, pdf_file_name, file_meta):
    """
    :function insert_file_in_pdf: Insert an image file in a PDF file.
    :param file_dir: path of input file, also the output file would be placed here.
    :param pdf_file_name: PDF in which Image needs to place.
    :param file_meta: Image data redden by any image processing tools.
    :return: Status of Operation, Name of output file
    """
    pdf_file = fitz.open(file_dir + pdf_file_name)
    counter = 0
    try:
        prefix_ = "final"
        if len(file_meta):
            img_formats = ['png', 'jpg']
            for page in pdf_file:
                file_name, file_page = list(file_meta[counter].items())[0]
                file_name_split = file_name.split('.')
                if page.number == file_page:
                    if file_name_split[1] in img_formats:
                        try:
                            rect = fitz.Rect(0, 0, 600, 620)
                            img = fitz.Pixmap(file_dir + file_name)
                            page.insertImage(rect, pixmap=img)
                            pdf_file.saveIncr()
                        except Exception as img_e:
                            # log.error(f'Exception in reading or inserting image {file_name}, MSG: {str(img_e)}')
                            pass
                    counter += 1
                if counter == len(file_meta): break
        file_start_name = prefix_+'_'+str(date.today())+'_'
        output_filename = file_dir + file_start_name + pdf_file_name
        pdf_file.save(output_filename)
        return True, output_filename  # file_start_name + pdf_file_name
    except Exception as e:
        print(str(e))
        return False, e


def ext_page_nums(page_nums, page_range, final_page_nums):
    """
    An internal function
    :function ext_page_nums: Extract a number of pages from input pdf and provides a new PDF.
    :param page_nums: Mention list of page numbers needs to extract.
    """
    for page_num in page_range:
        final_page_nums.append(page_num)
    # page_nums.remove(page_range)
    return page_nums


def extract_pdf_with_order(file_dir, input_file_name, page_nums):
    """
    An internal function
    :function extract_pdf_with_order: Extract numbers from pages of input pdf file.
    :param file_dir: path of input file, also the output file would be placed here.
    """
    image_meta = []
    try:
        read_pdf = PdfFileReader(file_dir + input_file_name)
        write_pdf = PdfFileWriter()

        new_filename = input_file_name.replace('.pdf', '_temp.pdf')
        # print(page_nums)
        final_page_nums = []
        for page in page_nums:
            # print('********************page************',page)
            if isinstance(page, range):
                page_nums = ext_page_nums(page_nums, page, final_page_nums)
            elif isinstance(page, list) and isinstance(page[0], str):
                # print(page_nums)
                page_nums = ext_page_nums(page_nums, page, final_page_nums)
            else:
                final_page_nums.append(page)

        for page in final_page_nums:
            if isinstance(page, str):
                img_formats = ['png', 'jpg']
                pdf_formats = ['pdf']
                # print(f'page:{page}')
                file_extension = page.split('.')[1]
                if file_extension in img_formats:
                    write_pdf.addBlankPage(width=600, height=650)  # comment------
                    # print("blank page added",write_pdf.getNumPages())
                    image_meta.append({page: write_pdf.getNumPages() - 1})
                elif file_extension in pdf_formats:
                    try:
                        # insert pages with iteration from sub-attachments if got pdf
                        read_attachments = PdfFileReader(file_dir + page)
                        total_attachment_pages = read_attachments.getNumPages()
                        for atchmnt_page in range(total_attachment_pages):
                            write_pdf.addPage(read_attachments.getPage(atchmnt_page))
                    except Exception as pdf_e:
                        pass
                        # log.error(f'Exception in reading or inserting pdf {page}, MSG: {str(pdf_e)}')

            else:
                # print(page, 'is going to be inserted')
                write_pdf.addPage(read_pdf.getPage(page - 1))

        with open(file_dir + new_filename, 'wb') as output_pdf:
            write_pdf.write(output_pdf)
            # output_pdf.close()
        # print(new_filename)
        return True, new_filename
    except Exception as e:
        print(traceback.print_exc())
        print(e)
        return False, ''


def generate_pdf(file_dir=None, output_filename='output.pdf', input_data=[]):
    """
    :function extract_pdf_with_order: Extract numbers from pages of input pdf file.
    :param file_dir: path of input file, also the output file would be placed here.
    :param output_filename: Name of Output file.
    :param input_data: Example is given below.
    :return: Status of operation.
    """
    copy_input_data = sorted(input_data.copy(), key=lambda i: i['order'])
    if not file_dir:
        file_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
    input_file_list = []
    status = False
    img_formats = ['png']
    pdf = ['pdf']
    try:
        # print('Start')
        for item in copy_input_data:
            for key, val in item.items():
                if key == 'pre_text':
                    new_filename = str(item['order']) + '.pdf'
                    _, txt_file_name = convert_text_to_pdf(new_filename, val)
                    input_file_list.append(txt_file_name)  # add file name into ordered list
                elif key == 'file':
                    input_file_name = val
                    split_file = val.rsplit('.', 1)
                    raw_file_name = split_file[0]
                    if split_file[-1].lower() in img_formats:
                        # Convert Image
                        _, new_filename = convert_img_to_pdf(file_dir, input_file_name, raw_file_name)
                        input_file_list.append(new_filename)  # add file name into ordered list
                    elif split_file[-1].lower() in pdf:
                        # Extract Number of pages from PDF
                        if 'pages' in item.keys():  # check for pages
                            page_nums = item['pages']
                            _, new_filename = extract_pdf_with_order(file_dir, input_file_name, page_nums)
                            input_file_list.append(new_filename)  # add file name into ordered list
                        else:  # Add Full PDF
                            input_file_list.append(input_file_name)  # add file name into ordered list
                    else:
                        # Needs to be handled
                        print('Neither Text/Image nor PDF')
        print(f'input_file_list::::{input_file_list}')
        if len(input_file_list):
            status = merge_pdfs(file_dir=file_dir, input_file_list=input_file_list,
                                output_filename=output_filename)  # Merge pdfs
            print('End with', status)
    except Exception as e:
        print('Exception-->', str(e))

    return status

# if __name__ == '__main__':
#     input_data = [{"pre_text": "Sam 1 \n Attachment 1", "file": "sam1.pdf", "order": 1},
#                   {"pre_text": "Sam 2 \n Attachment 2", "file": "sam2.pdf", "pages": [2, 4, range(6, 9)], "order": 4},
#                   {"pre_text": "Sam 3 \n Attachment 3", "file": "sam3.png", "order": 2},
#                   {"pre_text": "Sam 4 \n Attachment 4", "file": "sam4.pdf", "order": 3},
#                   # {"pre_text": "Sam 5 \n Attachment 5", "file": "sam5.xlsx", "order": 5}
#                   ]
#     status = generate_pdf(output_filename='output.pdf', input_data=input_data)

