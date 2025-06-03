from aiogram.fsm.state import State, StatesGroup

class SocraticFSM(StatesGroup):
    asking_questions = State()
    waiting_for_answer = State()
    done = State()
