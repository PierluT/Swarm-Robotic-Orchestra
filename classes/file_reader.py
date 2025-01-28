import csv

class File_Reader:
    
    def read_configuration_file(self):
        configuration_dictionary ={}
        file_path = "C:/Users/pierl/Desktop/MMI/tesi/robotic-orchestra/configuration_file.csv"
        
        with open(file_path, mode = 'r') as file:
            # csv reader
            csv_reader = csv.reader(file, delimiter=';')
            #read all the lines
            lines = list(csv_reader)
            parameters = lines[0]
            values = lines[1]
            #create a dictionary
            for parameters,values in zip(parameters,values):

                try:
                    values = int(values)
                except ValueError:
                    pass
                
                configuration_dictionary[parameters.strip()] = values

            return configuration_dictionary

         






