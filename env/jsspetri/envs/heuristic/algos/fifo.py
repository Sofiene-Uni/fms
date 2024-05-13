class Fifo():   
    "Remark : for a static jssp it empty the queue in ascending order one by one.In Dynamic JSSP fist in first out  "

    def __init__(self):
        self.label="FIFO"
        self.type_="static"
    def __str__(self):
       return  "First in first out (FIFO) , always return the enabled job with the lowest index."
    def decide(self,sim):
        mask =sim.action_masks()
        
        return min((index for index, value in enumerate(mask) if value), default=None)
    
    
    
    
    
        