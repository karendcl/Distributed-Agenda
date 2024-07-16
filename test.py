data = "kademlia.network - DEBUG - RESULT GET: [23543.546028162, \"{\'class\': \'event\', \'title\': \'IndepententE\', \'description\': \'\', \'date\': \'2024-07-19\', \'start_time\': \'15:00\', \'end_time\': \'16:00\', \'participants\': [\'shrimp1\', \'shrimp\'], \'groups\': [], \'event_id\': \'-8392381986752829950\', \'confirmed\': False, \'rejected\': False, \'pending_confirmations_people\': [\'shrimp\'], \'pending_confirmations_groups\': []}\"]"
if "kademlia.network" in data:
            # Find the index of the opening square bracket \'[\'
            start_index = data.find("{")
            
            # Find the index of the closing square bracket \']\'
            end_index = data.rfind("}") + 1
            
            data = data[start_index:end_index]
            print("Clean")

print(data)
