import os
import random
from mutagen import File
import pygame

import src.engine.constants as constants
import src.engine.game_state as game_state
from src.engine.helpers import load_settings, save_settings

# --- Music Settings Functions ---

def load_music_settings():
    """
    Load the music volume from the settings file.
    If not found, return the default music volume from constants.
    """
    settings = load_settings()
    try:
        volume = float(settings.get("music_volume", constants.music_volume))
        return max(0.0, min(1.0, volume))
    except Exception as e:
        print(f"Error loading music volume: {e}")
        return constants.music_volume

def save_music_settings(volume):
    """
    Save the music volume to the settings file.
    This updates only the 'music_volume' key.
    """
    settings = load_settings()
    settings["music_volume"] = volume
    save_settings(settings)

# --- Song/Playlist Settings Functions ---

def save_current_song_settings():
    """
    Save the current playlist and song indices into the settings file.
    This updates the keys 'current_playlist_index' and 'current_song_index'.
    """
    settings = load_settings()
    settings["current_playlist_index"] = game_state.current_playlist_index
    settings["current_song_index"] = game_state.current_song_index
    save_settings(settings)

def load_last_song_settings():
    """
    Load the last saved playlist and song indices from the settings file.
    Returns a dict with keys 'current_playlist_index' and 'current_song_index',
    or None if not present.
    """
    settings = load_settings()
    try:
        cp_index = int(settings.get("current_playlist_index", -1))
        cs_index = int(settings.get("current_song_index", -1))
        if cp_index >= 0 and cs_index >= 0:
            return {"current_playlist_index": cp_index, "current_song_index": cs_index}
        else:
            return None
    except Exception as e:
        return None

# --- Playlist and Song Functions ---

def load_all_playlists():
    """
    Return a list of subfolder names in assets/audio/.
    Each subfolder is treated as a separate playlist.
    """
    audio_base = "assets/audio"
    subfolders = [
        d for d in os.listdir(audio_base)
        if os.path.isdir(os.path.join(audio_base, d))
    ]
    return subfolders

def load_song_list_for(folder_name):
    """
    Given a folder name, return all .mp3 files inside assets/audio/<folder_name>.
    """
    song_folder = os.path.join("assets", "audio", folder_name)
    return [
        os.path.join(song_folder, f)
        for f in os.listdir(song_folder)
        if f.endswith('.mp3')
    ]

def play_current_song():
    """
    Play the song at game_state.song_list[game_state.current_song_index].
    Always start the song from the beginning.
    """
    if game_state.song_list:
        index = game_state.current_song_index
        song_path = game_state.song_list[index]
        game_state.current_song = song_path

        # Create a display string from the filename.
        base = os.path.basename(song_path)
        name_artist = os.path.splitext(base)[0]
        game_state.current_song_display = name_artist

        try:
            audio = File(song_path)
            duration = audio.info.length
        except Exception as e:
            print("Error reading audio info:", e)
            duration = 0

        pygame.mixer.music.load(song_path)
        pygame.mixer.music.set_volume(constants.music_volume)
        # Always start from the beginning (start_pos = 0)
        pygame.mixer.music.play(-1, start=0)

        # Save the current song settings so that this song will be resumed next time.
        save_current_song_settings()

def previous_song():
    """
    Go to the previous track in the current playlist.
    """
    if game_state.song_list:
        game_state.current_song_index = (game_state.current_song_index - 1) % len(game_state.song_list)
        play_current_song()

def next_song():
    """
    Go to the next track in the current playlist.
    """
    if game_state.song_list:
        game_state.current_song_index = (game_state.current_song_index + 1) % len(game_state.song_list)
        play_current_song()

def switch_playlist():
    """
    Switch to the next playlist (subfolder). Reset the song index to 0,
    then start playing the first song of the new playlist.
    """
    game_state.current_playlist_index = (game_state.current_playlist_index + 1) % len(game_state.playlist_folders)
    folder_name = game_state.playlist_folders[game_state.current_playlist_index]
    game_state.song_list = load_song_list_for(folder_name)
    game_state.current_song_index = 0
    play_current_song()

def load_and_play_music():
    """
    Initialize volume, load all playlists, and resume the last played song if possible.
    If no saved song exists, default to a random playlist and a random song.
    """
    try:
        constants.music_volume = load_music_settings()

        # Load all playlists (subfolders under assets/audio)
        game_state.playlist_folders = load_all_playlists()
        if not game_state.playlist_folders:
            raise Exception("No subfolders found in assets/audio.")

        # Try loading previous song settings
        last_settings = load_last_song_settings()
        if last_settings is not None:
            cp_index = last_settings.get("current_playlist_index")
            cs_index = last_settings.get("current_song_index")
            if cp_index is not None and cp_index < len(game_state.playlist_folders):
                game_state.current_playlist_index = cp_index
            else:
                game_state.current_playlist_index = random.randint(0, len(game_state.playlist_folders) - 1)
            current_playlist = game_state.playlist_folders[game_state.current_playlist_index]
            game_state.song_list = load_song_list_for(current_playlist)
            if game_state.song_list:
                if cs_index is not None and cs_index < len(game_state.song_list):
                    game_state.current_song_index = cs_index
                else:
                    game_state.current_song_index = random.randint(0, len(game_state.song_list) - 1)
            else:
                raise Exception(f"No songs found in folder: {current_playlist}")
        else:
            # No previous settings found, choose a random playlist and song
            game_state.current_playlist_index = random.randint(0, len(game_state.playlist_folders) - 1)
            current_playlist = game_state.playlist_folders[game_state.current_playlist_index]
            game_state.song_list = load_song_list_for(current_playlist)
            if not game_state.song_list:
                raise Exception(f"No songs found in folder: {current_playlist}")
            game_state.current_song_index = random.randint(0, len(game_state.song_list) - 1)

        play_current_song()

    except Exception as e:
        print(f"Error loading music: {e}")
