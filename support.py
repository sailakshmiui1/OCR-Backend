def validate_password(password):
    SpecialSym =['$', '@', '#', '%']
    
    if len(password) < 6:
        return 'Password length should be at least 6'
        
    if len(password) > 20:
        return 'Password length should be not be greater than 8'
        
    if not any(char.isdigit() for char in password):
        return 'Password should have at least one number'
        
    if not any(char.isupper() for char in password):
        return 'Password should have at least one uppercase letter'
        
    if not any(char.islower() for char in password):
        return 'Password should have at least one lowercase letter'
        
    if not any(char in SpecialSym for char in password):
        return 'Password should have at least one of the symbols $@#'
    
    return None