import os
from xlrd import open_workbook



root_dir = './data/xls'
target_dir = './data/txt_xls'



for subdir, dirs, files in os.walk(root_dir):
    dir_str = str.split(subdir,'/')
    for file in files:
        filename = os.path.join(subdir, file)
        txt_name = file[0:-4] + '.txt'
        print("File processing " + txt_name)
        
        try:                 
            # read from excel
            wb = open_workbook(filename)
            for s in wb.sheets():
                #print 'Sheet:',s.name
                content = ''
                for row in range(s.nrows):
                    # col_value = []
                    for col in range(s.ncols):
                        value  = (s.cell(row,col).value)
                        try : value = str(value)
                        except : pass
                        # col_value.append(value)
                        content = content + ' ' + value   

            # write in txt
            directory = target_dir
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            f = open(target_dir  +'/'+ txt_name,'w')
            f.write(content)
            f.close()               
            print("File processed " + str(txt_name))

        except: 
            f = open('xls_issues.txt','w')
            f.write(filename + '\n')   
            f.close()         
            pass

  