users = {
    "red_team_lead": {"role": "red_team", "clearance": 4, "department": "Red Team", "active": True},
    "blue_team_analyst": {"role": "blue_team", "clearance": 3, "department": "Blue Team", "active": True},
    "purple_team_coord": {"role": "purple_team", "clearance": 3, "department": "Purple Team", "active": True},
    "student_intern": {"role": "student", "clearance": 1, "department": "Academia", "active": True},
    "retired_expert": {"role": "retired", "clearance": 2, "department": "Emeritus", "active": False}
}

resources = [
    ("attack_scenarios", 4), ("defense_playbooks", 3),
    ("exercise_plans", 3), ("research_papers", 1), 
    ("exploit_tools", 4), ("student_resources", 1), 
    ("simulation_results", 3), ("red_team_tools", 4),
    ("blue_team_reports", 3), ("public_research", 1)
]

security_levels = ("Academic", "Operational", "Tactical", "Strategic")
blocked_users = {"retired_expert", "academic_violator", "leaked_account"}

def check_access():
    print("--- Список ресурсів ---")
    
    for res in resources:
        res_name = res[0]
        res_level = res[1]
        
        level_name = security_levels[res_level - 1]
        print(f"{res_name}: {level_name}")
        
    print("\n--- Результати перевірки доступу ---")
    
    users_to_test = [
        "red_team_lead", 
        "student_intern", 
        "retired_expert", 
        "academic_violator", 
        "unknown_hacker"
    ]
    
    for username in users_to_test:
        for res in resources:
            res_name = res[0]
            res_level = res[1]
            
            if username not in users:
                result = "DENY (User not found)"
                
            elif username in blocked_users:
                result = "DENY (User is blocked)"
                
            elif users[username]["active"] == False:
                result = "DENY (Account inactive)"
                
            elif users[username]["clearance"] >= res_level:
                result = "ALLOW"
                
            else:
                result = "DENY (Insufficient clearance)"
                
            print(f"user=[{username}] resource=[{res_name}] -> {result}")

if __name__ == "__main__":
    check_access()