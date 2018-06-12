class dataSlicingException(Exception):
    #User defined Exception class
    def __init__(self, task, signal, start_index, end_index, length):
        self.type = "dataSlicingException"
        self.task = task
        self.signal = signal
        self.start_index = start_index
        self.end_index = end_index
        self.length = length

    def print_exception_message(self):
        print("Exception Type: {} | Task: {} | Signal: {} | Start Index: {} End Index: {} | Length: {}".
              format(self.type, self.task, self.signal, self.start_index, self.end_index, self.length))



    #DEPRECATED CLASS!!!!!!!!!!!!!!!