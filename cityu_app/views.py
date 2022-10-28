from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import PngForm, ExcelForm
from .models import Png, Excel
from django.http import HttpResponse, FileResponse

from PyPDF2 import PdfFileReader, PdfFileWriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image

import pandas as pd
import shutil
import os
import traceback

# Create your views here.
@csrf_exempt
def upload_view(request):
    # clean up legacy file in ./media
    for root, dirs, files in os.walk('./media'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

    # clear legacy file in db
    Png.objects.all().delete()
    Excel.objects.all().delete()

    message = "CityU POD PDF Editor"


    # Handle file upload
    if request.method == 'POST':
        image_form = PngForm(request.POST, request.FILES)
        excel_form = ExcelForm(request.POST, request.FILES)
        date = request.POST["pod_month"]  # POD issue date set

        if image_form.is_valid() and excel_form.is_valid():
            # Image Handle #
            for file in request.FILES.getlist('pngfile'):  # loop for file in pngfile list
                imagedoc = Png(pngfile=file)  # assign variable "newdoc" to the uploaded Excel file
                imagedoc.save()

            # Excel Handle #
            exceldoc = Excel(excelfile=request.FILES['excelfile'])
            exceldoc.save()

            # Redirect to the document list after POST
            return pdf_export(request, date)
            # function ENDS

        else:
            message = 'The form is not valid. Fix the following error:'

    else:
        image_form = PngForm()  # An empty, unbound form
        excel_form = ExcelForm()  # An empty, unbound form


    # Render list page with the documents and the form
    context = {'image_form': image_form, 'excel_form': excel_form,'message': message}
    return render(request, 'cityu.html', context)



def pdf_export(request, date):
    try:
        # Create CityU_POD_temp and CityU_POD_pdf directories
        os.mkdir('./media/CityU_POD_temp')
        os.mkdir('./media/CityU_POD_pdf')

        # Set Excel
        xlsx_name = str(Excel.objects.all())[19:-3]
        xlsx = pd.read_excel(f'./media/{xlsx_name}')

        # Read Order Number
        order_num = []  # an empty list storing order numbers
        for i in range(0, len(xlsx['Order Number'])):  # loop for each order
            order_num.append(xlsx['Order Number'][i])

        # Read Order Timestamp
        order_timestamp = []  # an empty list storing timestamp
        for i in range(0, len(xlsx['Successful Date'])):  # loop for each order
            order_timestamp.append(str(xlsx['Successful Date'][i]))

        # Image --> pdf function
        for i in range(0, len(order_num)):
            image = Image.open(
                r'./media/CityU_POD/' + order_num[i] + '.png')  # tend to change
            pdf = image.convert('RGB')
            pdf.save(
                r'./media/CityU_POD_temp/' + order_num[i] + '.pdf')  # tend to change

        for i in range(0, len(order_num)):
            packet = io.BytesIO()  # create object packet in class _io.BytesIO
            can = canvas.Canvas(packet, pagesize=letter)  # Create a canvas of a given size

            # Set Text background color
            can.setFillColorRGB(1, 0.5, 0)  # background color
            can.rect(0, 0, 300, 100, fill=1)  # position of the block (anchor at bottom left corner)

            can.setFillColorRGB(0, 0, 0)  # text color
            can.setFont("Times-Roman", 23)  # text font and size
            can.drawString(10, 75, "ref: " + order_num[i])  # order_num content and position
            can.drawString(10, 25, order_timestamp[i])  # order_timestamp content and position
            can.save()  # save the temporary pdf containing timestamp info

            # move to the beginning of string io buffer
            packet.seek(0)

            # create a new pdf with timestamp info
            new_pdf = PdfFileReader(packet)

            # assign variable to original pdf
            existing_pdf = PdfFileReader(
                open(r'./media/CityU_POD_temp/' + order_num[i] + '.pdf',
                     "rb"))  # should be same as line 21

            # create a pdf that will merge the above two
            output = PdfFileWriter()
            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))  # merge page
            output.addPage(page)

            outputStream = open(r'./media/CityU_POD_pdf/' + order_num[i] + '.pdf',
                                "wb")  # can change output directory, adding r'{path}'
            output.write(outputStream)  # Writes the collection of pages added to this object out as a PDF file
            outputStream.close()

        # Download the CityU_POD_pdf file
        shutil.make_archive(f'./media/{date}_CityU_POD_pdf', 'zip', './media/CityU_POD_pdf')
        zip_file = open(f'./media/{date}_CityU_POD_pdf.zip', 'rb')

        # Clean Up Afterwards, act as redundancy
        shutil.rmtree('./media/CityU_POD')
        shutil.rmtree('./media/CityU_POD_temp')
        shutil.rmtree('./media/CityU_POD_pdf')
        os.remove(f'./media/{xlsx_name}')

        return FileResponse (zip_file)


    except Exception as e:
        # Clean the media file no matter what
        for root, dirs, files in os.walk('./media'):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        return HttpResponse(str(e) + '<br><br>' + 'Please prepare the missing .png if necessary and go back upload everything again.')




    # os.remove('/users/kelvin/desktop/pycharm/pdf_edit_ii/CityU_POD/' + order_num[i] + '.png')  # to check for uncommented png in excel



