
from .fifo import Fifo
from .lifo import Lifo

from .spt import Spt
from .lpt import Lpt

from .lptn import Lptn
from .sptn import Sptn

from .mtwr import Mtwr
from .ltwr import Ltwr 

from .sps import Sps
from .lps import Lps

from .spsr import Spsr
from .lpsr import Lpsr

from .swt import Swt
from .lwt import Lwt


def info(acronym):
    explanations = {
        "FIFO": "(First in first out)-Static: always returns the enabled job with the lowest index.",
        "LIFO": "(Last in first out)-Static: always returns the enabled job with the highest index.",
        "SPT": "(Shortest processing time)-Static: Prioritizes jobs with the initial shortest processing time.",
        "LPT": "(Longest processing time)-Static: Prioritizes jobs with the initial Longest processing time.",
        "SPS": "(Shortest Process Sequence)-Static: Prioritizes jobs with the least initial operations in the job queue.",
        "LPS": "(Longest Process Sequence)-Static: Prioritizes jobs with the most initial operations in the job queue.",
        "LTWR": "(Least Total Work remaining)-Dynamic: Prioritizes jobs with the least total work remaining (sequence * processing times) in the job queue.",
        "MTWR": "(Most Total Work remaining)-Dynamic: Prioritizes jobs with the most work remaining (sequence * processing_time) in the job queue.",
        "SPSR": "(Shortest Process Sequence remaining)-Dynamic: Prioritizes jobs with the least operations remaining in the job queue.",
        "LPSR": "(Longest Process Sequence Remaining)-Dynamic: Prioritizes jobs with the most operations remaining in the job queue.",
        "SPTN": "(Shortest Processing Time Next OP)-Dynamic: Selects the job with operation that is ready to be processed next and has the Shortest processing time.",
        "LPTN": "(Longest Processing Time Next OP)-Dynamic: Selects the job with operation that is ready to be processed next and has the Longest processing time.",
        "SWT" : "(Shortest Waiting Time)-Dynamic: Prioritize jobs with the lowest waiting time since last allocation",
        "LWT" : "(Longest Waiting Time)-Dynamic: Prioritize jobs with the higest waiting time since last allocation",
    }
    return explanations.get(acronym, "Explanation not available for the provided acronym.")



def init_heuristics(elite):
     
      algos = {
          
          0: Mtwr,
          1: Sptn,
          2: Lpsr,
          3: Lpt,
          4: Lps,
          5: Sps,
          6: Fifo,
          7: Lwt,
          8: Swt,
          9: Lifo,
          10: Spt,
          11: Spsr ,
          12: Lptn,
          13: Ltwr, 
         }
    
      if elite == None :
          heuristic_obj=[algos[idx]() for idx in algos ]
      else :
        heuristic_obj=[algos[idx]() for idx in range (elite)]
        
      
      return  heuristic_obj

def heuristic_index(algorithm_label):
     
      algos = {
         "MTWR" : 0,
         "SPTN" : 1,
         "LPSR" : 2 ,
         "LPT"  : 3 ,
         "LPS"  : 4,
         "SPS"  : 5,
         "FIFO" : 6,
         "LWT"  : 7,
         "SWT"  : 8,
         "LIFO" : 9 ,
         "SPT"  : 10,
         "SPSR" : 11,  
         "LPTN" : 12,
         "LTWR" : 13,
      }
      return  algos[algorithm_label]
     


   
   #---------------------------------------old order ------------------------------
 # def heuristic_index(algorithm_label):
     
 #     algos = {
 #        "FIFO" : 0,
 #        "LIFO" : 1,
 #        "SPT"  : 2 ,
 #         "LPT" : 3 ,
 #         "SPS" : 4,
 #        "LPS"  : 5,
 #         "SPSR": 6,
 #        "LPSR" : 7,
 #        "SPTN" : 8,
 #         "LPTN": 9 ,
 #        "LTWR" : 10,
 #        "MTWR" : 11,  
 #        "LWT"  : 12,
 #        "SWT"  : 13,
 #     }
 #     return  algos[algorithm_label]
     
 # def init_heuristics():
     
 #     algos = {
         
        
 #         0: Fifo,
 #         1: Lifo,
 #         2: Spt,
 #         3: Lpt,
 #         4: Sps,
 #         5: Lps,
 #         6: Spsr,
 #         7: Lpsr,
 #         8: Sptn,
 #         9: Lptn,
 #         10: Ltwr,
 #         11: Mtwr,  
 #         12: Lwt,
 #         13: Swt,
 #     }
     
 #     heuristic_obj=[algos[idx]() for idx in algos ]
     
 #     return  heuristic_obj
  
   
   
