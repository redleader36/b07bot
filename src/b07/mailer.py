import ConfigParser

# For sending email from python
import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

def emailKMLFile(alias, email, configFile):
    msg = MIMEMultipart()
    
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser(configFile))
    from_email = config.get('emailserver','email')
    password = config.get('emailserver','password')
    host = config.get('emailserver','hostname')
    port = int(config.get('emailserver','port'))
    msg['From'] = "Ingress Inventory No Reply <"+from_email+">"
    msg['To'] = email
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Ingress Inventory KML File"
    files = [os.path.expanduser("~/"+alias+"_keys.kml")]
    text = "<html><boody>Hi Agent "+alias+",<br>Attached is a copy of your keys in a kml file format, which can be imported into google maps.<br>"
    file = open(os.path.expanduser("~/"+alias+"_gear.html"),'rb')
    for line in file.readlines():
        text += line
    text += "The Ingress Inventory Team</body></html>"
    msg.attach( MIMEText(text, 'html'))
    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
        msg.attach(part)
    
    server = smtplib.SMTP(host,port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(from_email,password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.close()
    
def emailVersionUpdate(alias, email, configFile):
    msg = MIMEMultipart()
    
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser(configFile))
    from_email = config.get('emailserver','email')
    password = config.get('emailserver','password')
    host = config.get('emailserver','hostname')
    port = int(config.get('emailserver','port'))
    msg['From'] = "Ingress Inventory No Reply <"+from_email+">"
    msg['To'] = email
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Ingress Server Version Update"
    files = [os.path.expanduser("~/"+alias+"_config_old.cfg"),os.path.expanduser("~/"+alias+"_config.cfg")]
    text = "<html><boody>Hi Agent "+alias+",<br>The Server Version has been updated.<br><br>"
    file = open(os.path.expanduser("~/.ingress_server_version"),'rb')
    for line in file.readlines():
        text += line.strip()+"<br><br>"
    text += "The Ingress Inventory Team</body></html>"
    msg.attach( MIMEText(text, 'html'))
    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
        msg.attach(part)
    
    server = smtplib.SMTP(host,port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(from_email,password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.close()