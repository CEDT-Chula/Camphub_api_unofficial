from camp_parser import camphub_parser # or any thing taht we support
camp = camphub_parser('https://www.camphub.in.th/computer/') #page url
print(camp.info[0]['title']) #get the information