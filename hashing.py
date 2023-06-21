from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash():
    @staticmethod
    def bcrypt(Password:str):
        return pwd_context.hash(Password)
    @staticmethod
    def verified(plain_password,hashed_password):
        return pwd_context.verify(plain_password,hashed_password)