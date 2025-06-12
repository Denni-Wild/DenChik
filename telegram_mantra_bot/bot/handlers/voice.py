from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import tempfile
import os
import subprocess
import speech_recognition as sr
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.voice)
async def handle_voice_message(message: Message):
    logger.info(f'[VOICE] Получено голосовое сообщение вне FSM от пользователя {message.from_user.id}')
    # Скачиваем голосовое сообщение
    voice = message.voice
    file = await message.bot.get_file(voice.file_id)
    with tempfile.TemporaryDirectory() as tmpdir:
        ogg_path = os.path.join(tmpdir, 'voice.ogg')
        wav_path = os.path.join(tmpdir, 'voice.wav')
        await message.bot.download(file, destination=ogg_path)
        # Конвертируем ogg в wav с помощью ffmpeg
        try:
            subprocess.run([
                'ffmpeg', '-y', '-i', ogg_path, wav_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            await message.reply('Ошибка конвертации аудио. Проверьте, установлен ли ffmpeg.')
            return
        # Распознаём речь
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language='ru-RU')
                logger.info(f'[VOICE] Расшифрованный текст голосового запроса пользователя {message.from_user.id}: {text}')
                await message.reply(f'Распознанный текст: {text}')
            except sr.UnknownValueError:
                await message.reply('Не удалось распознать речь.')
            except sr.RequestError:
                await message.reply('Ошибка сервиса распознавания.') 