class Lifo():  
    "Remark : for a static jssp it empty the queue in decending order one by one.In Dynamic JSSP Last in first out "

    def __init__(self):
        self.label="LIFO"
        self.type_="static"
    def __str__(self):
       return  "Last in first out (LIFO) : always return the enabled job with the higest index."
    def decide(self,sim):
        mask =sim.action_masks()
        
        return max((index for index, value in enumerate(mask) if value), default=None)
    
    
    
    
    