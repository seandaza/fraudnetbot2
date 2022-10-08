
from flask import Flask
import chromedriver_binary  # Adds chromedriver binary to path
import os
import sys
import time
import smtplib
import pandas as pd
from base64 import encode
from datetime import datetime
from selenium import webdriver
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from selenium.webdriver.common.by import By
from email.mime.multipart import MIMEMultipart
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# The following options are required to make headless Chrome
# work in a Docker container
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1024,768")
chrome_options.add_argument("--no-sandbox")

# Initialize a new browser
browser = webdriver.Chrome(chrome_options=chrome_options)


@app.route("/")
def hello_bot():

    now = datetime.now() 
    year_month_day = now.strftime("%Y-%m-%d")
    
    driver = webdriver.Chrome(chrome_options=chrome_options)

    #set url feed for login
    url = 'https://network.americanexpress.com/globalnetwork/v4/sign-in/'

    payload={
        "Email": 'anastasiareyes1987',
        "Password": 'Casa1234??'
    }


    #Navigate to the page
    driver.get(url)
    driver.maximize_window()



    user_ID = driver.find_element("xpath", "//*[@id='userid']")
    user_ID.send_keys(payload['Email'])

    password = driver.find_element("xpath", "//*[@id='password']")
    password.send_keys(payload['Password'])
    time.sleep(2)

    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(1)

                                                
    signin_button = driver.find_element("xpath", '//*[@id="submit"]')
    #time.sleep(2
    signin_button.click()
    time.sleep(1)

    #Go to FraudNet Reports
    #Link only for 'Active' status reports
    new_url = "https://gnsfraudnet.americanexpress.com/fraudnet/#/ior/new"
    time.sleep(2)

    



    driver.get(new_url)
    time.sleep(2)
    #search_button = driver.find_element("xpath", "//button[@class='button primary pull-right margin-right']")
    #search_button.click()

    time.sleep(2)

    #scroll top down
    driver.execute_script("window.scrollTo(0, 300);")
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    #xpaths of the reports
    tbody = driver.find_element("xpath", '//*[@id="responsiveWrapper_sub"]/div[3]/div[2]/div/div/div[2]/div[2]/div/div[2]/table/tbody')

    #identify the number of rows or reports
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    print("numero de Reportes: ",len(rows))

    #Create a dataframe to store the data
    total_rows = []
    for j in range(1,len(rows) + 1):
        row = []
        for i in range(1,8):
            celda = driver.find_element("xpath",'//*[@id="responsiveWrapper_sub"]/div[3]/div[2]/div/div/div[2]/div[2]/div/div[2]/table/tbody/tr['+str(j)+']/td['+str(i)+']').get_attribute('innerHTML').replace("\n",'').strip()
            row.append(celda)
        total_rows.append(row)
    print(total_rows)

    #Declare the dataframe
    df = pd.DataFrame(total_rows)
    df.columns = ['CM Number','Token Number','Time Of Transaction','Amount (USD)','SE Number','SE Name','Rule Number']
    print(df)
    df.to_csv('all_reports.csv', index=False)
    print("fecha actual: ",year_month_day)

        
    #Validate new reports:
    new_reports = []
    for i in range(len(rows)):
        if total_rows[i][2][0:10] == year_month_day[0:10] and total_rows[i][0][0:6] == '379533':
            new_reports.append(total_rows[i])
            pass
        else:
            print("No new reports")
    print("New reports: ",new_reports)
    if len(new_reports) > 0:
            print("there are new reports")
            #declare and build the dataframe
            df2 = pd.DataFrame(new_reports)
            df2.columns = ['CM Number','Token Number','Time Of Transaction','Amount (USD)','SE Number','SE Name','Rule Number']
            #save the dataframe to a csv file with the last reports
            df2.to_csv('FraudNet_new_report_' + year_month_day + '.csv', index=False)

            #Send email with the new reports
            #screen shot and save in local
            driver.save_screenshot('new_report.png')

            #send email
            # create message object instance
            recipients = ['seandaza@gmail.com']#,'anastasiar@keoworld.com','carlosr@keoworld.com','carlosb@keoworld.com','ricardof@keoworld.com','armandoi@keoworld.com','luist@keoworld.com','edissonv@keoworld.com','erikab@keoworld.com', 'jhand@keoworld.com']
            for elm in recipients:
                msg = MIMEMultipart()
                # setup the parameters of the message
                password = "kvjxjjghzpqfdpcd"
                msg['From'] = "jhand@keoworld.com"
                msg['Subject'] = "FraudnetBot Alert: new report(s) found"
                msg['To'] = f"{elm}"
                
                # attach image and text to message body
                for i in range(len(new_reports)):
                    msg.attach(MIMEText('New Report Found: '+ '\n' +
                    'CM NUMBER:' + '\t' + str(new_reports[i][0]).replace("'",'') + '\n' +
                    'TOKEN NUMBER:' + '\t' + str(new_reports[i][1]).replace("'",'') + '\n' +
                    'TIME OF TRANSACTION:' + '\t' + str(new_reports[i][2]).replace("'",'') + '\n' +
                    'AMOUNT (USD):' + '\t' + str(new_reports[i][3]).replace("'",'') + '\n' +
                    'SE NUMBER:' + '\t' + str(new_reports[i][4]).replace("'",'') + '\n' +
                    'SE NAME:' + '\t' + str(new_reports[i][5]).replace("'",'') + '\n' +
                    'RULE NUMBER:' + '\t' + str(new_reports[i][6]).replace("'",'') +'\n' +
                    '------------------------------------------------------------------'+
                    '\n\n'))
                msg.attach(MIMEImage(open('new_report.png', 'rb').read()))
                
                # create server
                server = smtplib.SMTP('smtp.outlook.com: 587')
                server.starttls()
                
                # Login Credentials for sending the mail
                server.login(msg['From'], password)
                
                # send the message via the server.
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                
                server.quit()
                print("Email sent successfully")
    else:
        print("No new reports")
        pass
    time.sleep(1)
    driver.quit()
    return df2
