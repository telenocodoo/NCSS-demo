from odoo import api, models, _
import re

class letterDynamicReport(models.AbstractModel):
    _name = 'report.hr_employee_letter.letter_report_template'
    _description = 'Letter Report'

    @api.model
    def _get_report_values(self, docids, data=None):


        print("docids",docids[0])

        docs = self.env['letter.request'].browse(docids[0])
        my_list = []
        for app in docs:
            vals = {
                'request_id':app.request_id.id,
                'name': app.name,
                'temp': app.letter_type_id.template_id,
                'model': app.letter_type_id.model,

            }
            my_list.append(vals)

        print(my_list)
        mydata=my_list[0]
        myemp =self.env[mydata['model']].search([('id','=',mydata['request_id'])])
        str=mydata['temp']
        newstr=str
        # get list_item

        list1 = []
        startpos = 0
        while True:
            first_index = str.find('${object.', startpos)

            if first_index == -1:
                break
            second_index = str.find('}', startpos)

            myword = str[first_index:second_index + 1]
            mynewWord=str[first_index+9:second_index]
            x = myemp.mapped(mynewWord)

            print(x[0])
            newstr=newstr.replace(myword,x[0])

            print(first_index, second_index, myword)
            list1.append(mynewWord)
            startpos = second_index + 1
        #

        print( "result",list1)
        print("hello shaliby",newstr)

        mydata['temp']=newstr
        return {
            'doc_model': 'letter.request',
            'docs': docs,
            'my_list': my_list,
        }
