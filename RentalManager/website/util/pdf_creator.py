from fpdf import FPDF
import codecs
from datetime import datetime
from configparser import ConfigParser
from ..database import db_service
from ..database.models import Guest, Booking, Flat
import uuid
import os

class PDF(FPDF):
    def footer(self):
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        # Select Arial italic 8
        self.set_font('Times', '', 12)
        # Print centered page number
        f = codecs.open('Mietvereinbarung/Footer.txt', 'r', 'utf-8')
        text = f.read()
        f.close()
        self.multi_cell(0, 5, text, border="T", align='C')


class Agreement():
    def __init__(self, booking: Booking):
        guest = db_service.get_guest_by_id(booking.guest_id)
        flat = db_service.get_flat_by_id(booking.flat_id)
        self.prename = guest.prename
        self.surname = guest.surname
        self.street = guest.street_name
        self.house_number = guest.house_number
        self.postcode = guest.postcode
        self.city = guest.city
        self.holiday_flat = flat.name
        self.persons = booking.number_persons
        self.pets = booking.number_pets
        self.start_date = booking.start_date
        self.end_date = booking.end_date
        self.nights = (booking.end_date - booking.start_date).days
        self.price = booking.price  

    def get_running_number(self):
        parser = ConfigParser()
        parser.read('config.ini')
        if parser.get('NUMBER', 'date') == str(datetime.now().strftime("%Y%m%d")):
            old = int(parser.get('NUMBER', 'number'))
            new = old + 1
            parser.set('NUMBER', 'number', str(new))
            # Writing our configuration file to 'example.ini'
            with open('config.ini', 'w') as f:
                parser.write(f)
            return str(new)
        else:
            new = '0'
            parser.set('NUMBER', 'number', new)
            parser.set('NUMBER', 'date', str(
                datetime.now().strftime("%Y%m%d")))
            # Writing our configuration file to 'example.ini'
            with open('config.ini', 'w') as f:
                parser.write(f)
            return new

    def create_bill_name(self, id):
        start = str(self.start_date.strftime("%d-%m-%Y").replace('.', ''))
        end = str(self.end_date.strftime("%d-%m-%Y").replace('.', ''))
        file_name = "Rechnung_" + str(id) + "_" + "Borkum" + self.holiday_flat + "_" + self.surname + start + "b" + end + '.pdf'
        return file_name

    def create_filename(self):
        start = str(self.start_date.strftime("%d-%m-%Y").replace('.', ''))
        end = str(self.end_date.strftime("%d-%m-%Y").replace('.', ''))
        file_name = "Übersicht_" +  "_" + "Borkum" + "_" + self.holiday_flat + "_" + self.surname + start + "b" + end + '.pdf'
        return file_name

    def create_overview(self):
        pdf = PDF(orientation='P', format='A4')
        pdf.set_margins(25, 25)
        pdf.add_page()

        # Überschrift
        pdf.set_font('Times', 'B', 14)
        pdf.multi_cell(0, 5, "Anfrage\n\n", align='C')
        
        pdf.set_font('Times', '', 12)
        # Buchungsinformationen
        text = ""
        text = text + "Name:  " + str(self.prename) + " " + str(self.surname) + "\n"
        text = text + "Wohnung:  " + str(self.holiday_flat) + "\n"
        text = text + "Von:  " + str(self.start_date.strftime("%d-%m-%Y")) + "\n"
        text = text + "Bis:  " + str(self.end_date.strftime("%d-%m-%Y")) + "\n"
        text = text + "Nächte:  " + str(self.nights) + "\n"
        text = text + "Anzahl Personen:  " + str(self.persons) + "\n"
        text = text + "Anzahl Haustiere:  " + str(self.pets) + "\n \n"
        pdf.multi_cell(0, 5, text, align='L')
        # Preis
        pdf.set_font('Times', 'B', 12)
        text = "Preis:" + "\n"
        pdf.multi_cell(0, 5, text, align='L')

        pdf.set_font('Times', '', 12)
        text = ""
        text = text + "Gesamt: " + str(self.price) + "\n"
        text = text + "Anzahlung: " + str(self.price*0.25) + "\n"
        text = text + "Rest: " + str(self.price*0.75) + "\n \n"
        pdf.multi_cell(0, 5, text, align='L')
        # Adresse
        pdf.set_font('Times', 'B', 12)
        pdf.multi_cell(0, 5, "Anschrift:", align='L')
        pdf.set_font('Times', '', 12)
        text = self.street + " " + str(self.house_number) + "\n " +  str(self.postcode) + " " + self.city
        pdf.multi_cell(0, 5, text, align='L')

        return pdf

    def create_agreement(self):
        
        name = self.prename + " " + self.surname
        pdf = PDF(orientation='P', format='A4')
        pdf.set_margins(25, 25)
        pdf.add_page()

        pdf.set_font('Times', '', 12)
        path = os.path.relpath("Mietvereinbarung")

        # Anschrift Angela
	
        f = open(os.path.join(path, 'Header_Angela.txt'), 'r')
        text = f.read().split("\n")
        f.close()
        for t in text:
            pdf.cell(0, 5, t, ln=2, align='R')

        # Gast
        f = codecs.open('/Mietvereinbarung/Header_Gast.txt', 'r', 'utf-8')
        text = f.read().split("\n")
        f.close()
        for t in text:
            pdf.cell(0, 5, t, ln=2, align='L')

        # Ort, Datum
        text = "Friedrichsfehn, den " + \
            str(datetime.now().strftime("%d.%m.%Y"))
        pdf.cell(0, 5, text, ln=2, align='R')

        # Überschrift
        text = "\nBetr.: Ihr Aufenthalt in unserer Ferienwohnung  auf Borkum \n "
        pdf.set_font('Times', 'B', 12)
        pdf.multi_cell(0, 5, text, align='L')

        # Info
        f = codecs.open('Mietvereinbarung/Info.txt', 'r', 'utf-8')
        text = f.read()
        f.close()
        pdf.set_font('Times', '', 12)
        pdf.multi_cell(0, 5, text, align='L')

        pdf.add_page()

        # Anschrift
        text = name + ", " + self.street + " " + \
            str(self.house_number) + ", " + \
            str(self.postcode) + " " + self.city + "\n \n \n "
        pdf.set_font('Times', '', 12)
        pdf.multi_cell(0, 5, text, align='L')

        # Anschrift Angela
        text = "Angela Scheibe \nRüschenweg 46 \n26188 Edewecht"
        pdf.set_font('Times', '', 12)
        pdf.multi_cell(0, 5, text, align='L')

        # Ort, Datum
        text = self.city + ", den                      "
        pdf.cell(0, 5, text, ln=2, align='R')

        # mietvereinbarung
        text = "\nMietvereinbarung\n "
        pdf.set_font('Times', 'B', 14)
        pdf.multi_cell(0, 5, text, align='C')

        text = "Ich bestätige, dass ich Ihre Ferienwohnung " + chr(34) + \
            self.holiday_flat + chr(34) + " (Borkum, Greune-Stee-Weg 43) vom "
        pdf.set_font('Times', '', 12)
        pdf.multi_cell(0, 5, text, align='L')

        text = self.start_date.strftime("%d-%m-%Y") + " bis zum " + self.end_date.strftime("%d-%m-%Y")
        pdf.set_font('Times', 'B', 12)
        pdf.multi_cell(0, 5, text, align='C')

        text = "mieten werde. (" + str(self.nights) + " Übernachtungen)"
        pdf.set_font('Times', '', 12)
        pdf.multi_cell(0, 5, text, align='L')

        text = "Die Miete (ohne Kurbeitrag) beträgt:"
        pdf.multi_cell(0, 5, text, align='L')

        text = str(self.price).replace('.', ',') + chr(128) + \
            " Wohnungsmiete (inkl. Bettwäsche/Handtücher für " + \
            str(self.persons) + " Pers."
        if int(self.pets) > 0:
            text = text + " + " + \
                str(self.pets) + " Haustier/e)"
        else:
            text = text + ")"
        pdf.multi_cell(0, 5, text, align='L')

        text = "Eine Anzahlung auf den Mietpreis in Höhe von 25% (" + str(
            self.price*0.25).replace('.', ',') + chr(128)+") werde ich sofort überweisen, den Restbetrag 4 Wochen vor Beginn des Buchungszeitraums. \nDes Weiteren werde ich dafür Sorge tragen, dass das Rauchverbot in der Wohnung eingehalten und die Wohnung sauber und gereinigt verlassen wird. \n\n\n\n "
        pdf.multi_cell(0, 5, text, align='L')

        text = "Unterschrift \n\n "
        pdf.multi_cell(35, 5, text, border='T', align='L')

        text = "Mitreisende: \n         Vorname,   Nachname,   Geburtsdatum: "
        for i in range(0, self.persons):
            text = text + "\n\n" + str(i+1) + ". "
        pdf.multi_cell(0, 5, text, align='L')

        text = "\nFür den Rücktritt von dieser bestätigten Buchung gilt die Hotelordnung der Kurverwaltung Borkum. Diese sagt aus, dass der Mietpreis auch dann fällig ist, wenn die Wohnung nicht in Anspruch genommen wird und kein Ersatzmieter gefunden werden kann. Einsparungen von 10% werden angerechnet."
        pdf.multi_cell(0, 5, text, align='L')
        return pdf

