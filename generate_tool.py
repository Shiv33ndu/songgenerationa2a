from gradio_client import Client
import logging, time

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("songgen_proxy")

# Target (remote) SongGeneration space
REMOTE_SPACE = "tencent/SongGeneration"   # owner/space id
client = Client(REMOTE_SPACE, download_files=False)             # optional: Client(REMOTE_SPACE, hf_token="hf_xxx")


def proxy_generate(lyrics: str, description: str, genre: str, cfg_coef: float, temperature: float, duration_state: int=50, use_async: bool=False):
    """
    This is the Gradio callable. It calls the remote SongGeneration space and returns
    either a Gradio-playable filepath (so the UI can play it) and a JSON dict where 'audio_base64' is available.

    args:
        lyrics: str
        description: str,
        genre: str,
        cfg_coef: float,
        temperature: float,
        duration_state: int,
        use_async: bool

    return:
        file_url : Dict
    """
    args = [lyrics, description or "", None, genre or "Pop", cfg_coef or 1.5, temperature or 0.8, duration_state or 50]

    try:
        if use_async:
            job = client.submit(*args, api_name="/generate_song")
            # poll for completion (simple polling)
            t0 = time.time()
            while True:
                st = job.status()
                if st == "COMPLETED":
                    res = job.result()
                    break
                if st == "FAILED":
                    raise RuntimeError("Remote job failed")
                if time.time() - t0 > 120:   # 2 minute timeout default
                    raise TimeoutError("Remote job timed out")
                time.sleep(1.5)
        else:
            # synchronous call (blocks)
            res = client.predict(*args, api_name="/generate_song")
    except Exception as e:
        log.exception("Error calling remote SongGeneration")
        return {"error": str(e)}, None
    
    # the response is tuple({file_url},{input_data})
    return res[0]  # we return only url of the file for embedding purposes 

# Example of res[0]:
#{
# 'path': '/tmp/gradio/927ce3d5e86d0b7518af04d24a4b8251d9661c95/tmprv1uxutz.flac', 
# 'url': 'https://tencent-songgeneration.hf.space/file=/tmp/gradio/927ce3d5e86d0b7518af04d24a4b8251d9661c95/tmprv1uxutz.flac', 
# 'size': None, 
# 'orig_name': 'tmprv1uxutz.flac', 
# 'mime_type': None, 
# 'is_stream': False, 
# 'meta': {
#           '_type': 'gradio.FileData'
#          }
# }
