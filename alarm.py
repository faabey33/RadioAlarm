import spotipy
from spotipy.oauth2 import SpotifyOAuth
import schedule
import threading
import time
from fastapi import FastAPI

app = FastAPI()

def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def spotify_job():
   
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                                scope="user-library-read user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control"))

    results = sp.devices()
    print(results)

    sp.start_playback(device_id=radio_id, context_uri='spotify:playlist:25WhznxCMB3XARhPLwdLoM', uris=None, offset=None, position_ms=None)
    sp.shuffle(True, device_id=radio_id)
    sp.next_track(device_id=radio_id)


def dummy_job():
    pass



alarm_job = schedule.every().day.at("00:00").do(dummy_job)

@app.get("/setDisabled")
async def set_disabled():
    global alarm_job
    schedule.cancel_job(alarm_job)
    return {"disabled alarm:": "true"}

@app.get("/setAlarmTime/{time}")
async def set_alarm_time(time):
    global alarm_job
    time = time.replace("-",":")
    # cancel old job
    schedule.cancel_job(alarm_job)
    # set new job
    alarm_job = schedule.every().day.at(time).do(spotify_job)
    stop_run_continuously = run_continuously()
    return {"set Alarm Time to": time}

