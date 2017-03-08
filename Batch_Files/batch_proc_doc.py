import os
from docx import Document



root_dir = './data/docxs'
target_dir = './data/txt_docx'



for subdir, dirs, files in os.walk(root_dir):
    dir_str = str.split(subdir,'/')
    for file in files:
        filename = os.path.join(subdir, file)
        txt_name = file[0:-4] + 'txt'
        print("File processing " + txt_name)
        
        
        try:                
            # read from docx                     
            
            f = open(filename, 'rb')
            document = Document(f)
            f.close()
            
            content = ''
            for para in document.paragraphs:
                content = content + ' ' + para.text.encode('utf-8').strip()
                           
            # write in txt
            directory = target_dir
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            f = open(target_dir  +'/'+ txt_name,'w')
            f.write(content)
            f.close()               
            print("File processed " + str(txt_name))
        except: 
            f = open('docx_issues.txt','w')
            f.write(filename + '\n')      
            f.close()     
            pass

   