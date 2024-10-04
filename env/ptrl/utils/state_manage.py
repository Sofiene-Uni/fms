from ptrl.envs.fms.simulator import Simulator
from ptrl.common.build_blocks import  Token
import pickle

def save_state(sim):
    
   """
   Save the current state of all tokens.
   """
   state = {"clock":sim.clock ,"marking":{}}
   for place_uid, place in sim.places.items():
        if place.token_container:
            state["marking"][place_uid]=[]
            
            for token in place.token_container:
                
                token_dict={"uid":token.uid,
                            "type_":token.type_,
                            "role":token.role ,
                            "rank":token.rank,
                            "color":token.color,
                            "time_features":token.time_features,
                            "machine_sequence":token.machine_sequence,
                            "logging":token.logging
                            
                            }

                state["marking"][place_uid].append(token_dict)
            

   # with open('state.pkl', 'wb') as file:
   #      pickle.dump(state, file)
   # print("State saved successfully!")
   
   return   state 
   
   
   

   
def load_state(sim,state=None):
    
    
        """
        Load the state of tokens and reinitialize the Petri net with saved tokens.
        """
        
             
        # # Load the saved state from the file
        # if state== None:
        #     with open('state.pkl', 'rb') as file:
        #         state = pickle.load(file)
                
        #     print("State loaded successfully!")
     
        
        # Rebuild the empty Petri net structure
    
        twin=Simulator(label="twin",instance_id= sim.instance_id ,layout=sim.layout, n_agv=sim.n_agv , n_tt=sim.n_tt,) 
        twin.create_petri(show_flags=True)

        for place_uid, tokens in state ["marking"].items():
   
            for twin_place_uid, twin_place in twin.places.items():  
                if twin_place_uid== place_uid:
                  
                    for token in tokens:
      
                        token_obj = Token (uid = token["uid"] ,
                                           type_=token["type_"], 
                                           role=token["role"],
                                           rank=token["rank"], 
                                           color=token["color"],
                                           time_features=token["time_features"],
                                           machine_sequence=token["machine_sequence"]
                                          )
                        
                        token_obj.logging= token["logging"]
                        twin_place.token_container.append(token_obj)
                        
   
        twin.clock=state ["clock"]
      
        
        return twin