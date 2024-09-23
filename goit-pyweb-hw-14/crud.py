from sqlalchemy.orm import Session
from models import Contact, User
from schemas import ContactCreate, ContactUpdate
from passlib.context import CryptContext

from fastapi import HTTPException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_contact(db: Session, contact: ContactCreate, user_id: int):
    """
    Создаёт новый контакт в базе данных.
    
    Args:
        db (Session): Сессия базы данных.
        contact (ContactCreate): Данные нового контакта.
        user_id (int): ID пользователя, которому принадлежит контакт.

    Returns:
        Contact: Созданный контакт.
    """
    db_contact = Contact(**contact.dict(), user_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def create_user(db: Session, email: str, password: str):
    """
    Создаёт нового пользователя в базе данных.
    
    Args:
        db (Session): Сессия базы данных.
        email (str): Email нового пользователя.
        password (str): Пароль нового пользователя.

    Raises:
        HTTPException: Если email уже зарегистрирован.

    Returns:
        User: Созданный пользователь.
    """
    hashed_password = pwd_context.hash(password)
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    verification_token = create_access_token(data={"sub": str(new_user.id)}, expires_delta=timedelta(days=1))
    send_verification_email(email, verification_token)
    
    return new_user

def hash_password(password: str) -> str:
    """
    Хеширует пароль с использованием алгоритма bcrypt.
    
    Args:
        password (str): Пароль для хеширования.

    Returns:
        str: Хешированный пароль.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли данный пароль его хешу.
    
    Args:
        plain_password (str): Пароль в открытом виде.
        hashed_password (str): Хешированный пароль.

    Returns:
        bool: True, если пароль соответствует хешу, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_contact(db: Session, contact_id: int, user_id: int):
    """
    Получает контакт по его ID и ID пользователя.
    
    Args:
        db (Session): Сессия базы данных.
        contact_id (int): ID контакта.
        user_id (int): ID пользователя.

    Returns:
        Contact: Найденный контакт или None, если не найден.
    """
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """
    Получает список контактов для данного пользователя с возможностью пагинации.
    
    Args:
        db (Session): Сессия базы данных.
        user_id (int): ID пользователя.
        skip (int, optional): Количество пропущенных записей. По умолчанию 0.
        limit (int, optional): Максимальное количество возвращаемых контактов. По умолчанию 10.

    Returns:
        List[Contact]: Список контактов пользователя.
    """
    return db.query(Contact).filter(Contact.user_id == user_id).offset(skip).limit(limit).all()

def update_contact(db: Session, contact_id: int, contact: ContactUpdate, user_id: int):
    """
    Обновляет существующий контакт в базе данных.
    
    Args:
        db (Session): Сессия базы данных.
        contact_id (int): ID контакта для обновления.
        contact (ContactUpdate): Данные для обновления контакта.
        user_id (int): ID пользователя, которому принадлежит контакт.

    Returns:
        Contact: Обновлённый контакт или None, если контакт не найден.
    """
    db_contact = get_contact(db, contact_id, user_id)
    if db_contact is None:
        return None
    for key, value in contact.dict(exclude_unset=True).items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Удаляет контакт из базы данных по его ID и ID пользователя.
    
    Args:
        db (Session): Сессия базы данных.
        contact_id (int): ID контакта для удаления.
        user_id (int): ID пользователя, которому принадлежит контакт.

    Returns:
        Contact: Удалённый контакт или None, если контакт не найден.
    """
    db_contact = get_contact(db, contact_id, user_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact
